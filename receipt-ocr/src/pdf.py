"""PDF text extraction with a consistent PDF-point coordinate system.

Native PDF elements and OCR elements both use coordinates measured in PDF
points, with the origin at the page's top-left corner. OCR pixel coordinates
are scaled back to PDF points after a page is rendered.
"""

from __future__ import annotations

import os
from tempfile import TemporaryDirectory
from typing import Literal, Sequence, TypedDict

import pymupdf

from .ocr import OCRResult, extract_text

PDFElementSource = Literal["native_pdf", "ocr"]


class PDFElement(TypedDict):
    """A page element with coordinates in PDF points."""

    text: str
    confidence: float
    bbox: list[float] | list[list[float]]
    source: PDFElementSource


class PDFPageResult(TypedDict):
    """All extracted elements associated with a one-based PDF page number."""

    page: int
    elements: list[PDFElement]


def get_pdf_page_count(pdf_path: str) -> int:
    """Return the number of pages in a PDF document."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    with pymupdf.open(pdf_path) as document:
        return document.page_count


def _native_page_elements(page: pymupdf.Page) -> list[PDFElement]:
    elements: list[PDFElement] = []
    for block in page.get_text("blocks", sort=True):
        text = str(block[4]).strip()
        if not text:
            continue

        elements.append(
            {
                "text": text,
                "confidence": 1.0,
                "bbox": [float(block[0]), float(block[1]), float(block[2]), float(block[3])],
                "source": "native_pdf",
            }
        )
    return elements


def _convert_ocr_bbox_to_pdf_points(
    bbox: list[list[float]], page: pymupdf.Page, pixel_width: int, pixel_height: int
) -> list[list[float]]:
    scale_x = page.rect.width / pixel_width
    scale_y = page.rect.height / pixel_height
    return [
        [round(point[0] * scale_x, 2), round(point[1] * scale_y, 2)]
        for point in bbox
    ]


def _ocr_page_elements(page: pymupdf.Page) -> list[PDFElement]:
    """Render one page and map EasyOCR pixel boxes into PDF points."""
    matrix = pymupdf.Matrix(2.0, 2.0)
    pixmap = page.get_pixmap(matrix=matrix, alpha=False)

    with TemporaryDirectory() as temporary_directory:
        image_path = os.path.join(temporary_directory, "page.png")
        pixmap.save(image_path)
        ocr_results: list[OCRResult] = extract_text(image_path)

    return [
        {
            "text": result["text"],
            "confidence": result["confidence"],
            "bbox": _convert_ocr_bbox_to_pdf_points(
                result["bbox"], page, pixmap.width, pixmap.height
            ),
            "source": "ocr",
        }
        for result in ocr_results
    ]


def extract_pdf(
    pdf_path: str, pages: Sequence[int] | None = None
) -> list[PDFPageResult]:
    """Extract native text or OCR elements from selected one-based PDF pages.

    Pages with usable native text use PyMuPDF blocks. Pages without native text
    are rendered and sent through the existing EasyOCR pipeline. When ``pages``
    is omitted, every page is processed.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    with pymupdf.open(pdf_path) as document:
        page_numbers = list(pages) if pages is not None else list(
            range(1, document.page_count + 1)
        )
        if any(page_number < 1 or page_number > document.page_count for page_number in page_numbers):
            raise ValueError("PDF page numbers must be within the document page range")

        extracted_pages: list[PDFPageResult] = []
        for page_number in page_numbers:
            page = document[page_number - 1]
            elements = _native_page_elements(page)
            if not elements:
                elements = _ocr_page_elements(page)
            extracted_pages.append({"page": page_number, "elements": elements})

        return extracted_pages