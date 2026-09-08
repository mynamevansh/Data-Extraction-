"""Extract native PDF text, form fields, and page metadata.

Coordinates use PDF points with the origin at the top-left of each page.
Bounding boxes are ``[x0, y0, x1, y1]`` in the page's unrotated coordinate
space. This module reads native PDF structures only; it does not use OCR.
"""

from __future__ import annotations

import os
from collections import Counter
from typing import Any, TypedDict

import pymupdf


class PDFStructureElement(TypedDict):
    """A native text block or form field on a PDF page."""

    type: str
    text: str
    bbox: list[float]
    name: str
    field_type: str
    value: Any
    default_value: Any
    editable: bool
    field_flags: int


class PDFPageStructure(TypedDict):
    page: int
    width: float
    height: float
    elements: list[PDFStructureElement]


class PDFStructure(TypedDict):
    pages: int
    form_technology: str
    page_structures: list[PDFPageStructure]


def _bbox(rect: pymupdf.Rect) -> list[float]:
    return [round(float(value), 4) for value in (rect.x0, rect.y0, rect.x1, rect.y1)]


def _form_technology(document: pymupdf.Document) -> str:
    catalog_object = document.xref_object(document.pdf_catalog())
    if "/AcroForm" not in catalog_object:
        return "none"

    acroform_reference = catalog_object.split("/AcroForm", 1)[1].split()[0:2]
    if len(acroform_reference) >= 2 and acroform_reference[1] == "0":
        acroform_object = document.xref_object(int(acroform_reference[0]))
        if "/XFA" in acroform_object:
            return "AcroForm + XFA"
    return "AcroForm"


def _text_elements(page: pymupdf.Page) -> list[PDFStructureElement]:
    elements: list[PDFStructureElement] = []
    for block in page.get_text("dict", sort=True)["blocks"]:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = str(span.get("text", "")).strip()
                if not text:
                    continue
                elements.append(
                    {
                        "type": "text",
                        "text": text,
                        "bbox": [
                            round(float(value), 4) for value in span["bbox"]
                        ],
                        "name": "",
                        "field_type": "",
                        "value": None,
                        "default_value": None,
                        "editable": False,
                        "field_flags": 0,
                    }
                )
    return elements


def _field_elements(page: pymupdf.Page) -> list[PDFStructureElement]:
    elements: list[PDFStructureElement] = []
    for widget in page.widgets() or []:
        flags = int(widget.field_flags or 0)
        elements.append(
            {
                "type": "field",
                "text": "",
                "bbox": _bbox(widget.rect),
                "name": str(widget.field_name or ""),
                "field_type": str(widget.field_type_string or "Unknown"),
                "value": widget.field_value,
                "default_value": getattr(widget, "field_default_value", None),
                "editable": not bool(flags & 1),
                "field_flags": flags,
            }
        )
    return elements


def extract_pdf_structure(pdf_path: str) -> PDFStructure:
    """Return native text and form fields for every page in a PDF.

    The returned page numbers are one-based. Native field values and default
    values are included when exposed by PyMuPDF; unavailable defaults are
    represented as ``None``.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    with pymupdf.open(pdf_path) as document:
        page_structures: list[PDFPageStructure] = []
        for page_number, page in enumerate(document, start=1):
            page_structures.append(
                {
                    "page": page_number,
                    "width": round(float(page.rect.width), 4),
                    "height": round(float(page.rect.height), 4),
                    "elements": _text_elements(page) + _field_elements(page),
                }
            )

        return {
            "pages": document.page_count,
            "form_technology": _form_technology(document),
            "page_structures": page_structures,
        }


def field_type_counts(structure: PDFStructure) -> dict[str, int]:
    """Count native form fields by their PyMuPDF field type name."""
    return dict(
        Counter(
            element["field_type"]
            for page in structure["page_structures"]
            for element in page["elements"]
            if element["type"] == "field"
        )
    )