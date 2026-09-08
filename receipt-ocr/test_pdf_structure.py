"""Diagnostic for native FR Y-9C PDF structure and form fields."""

from __future__ import annotations

import json
from pathlib import Path

from src.pdf_structure import extract_pdf_structure, field_type_counts


PDF_FIXTURES = (Path("data/FR_Y9C.pdf"), Path("data/DownloadAttachment.pdf"))


def main() -> None:
    pdf_path = next((path for path in PDF_FIXTURES if path.is_file()), None)
    if pdf_path is None:
        raise FileNotFoundError("Expected data/FR_Y9C.pdf or data/DownloadAttachment.pdf")

    structure = extract_pdf_structure(str(pdf_path))
    pages = structure["page_structures"]
    fields = [
        element
        for page in pages
        for element in page["elements"]
        if element["type"] == "field"
    ]
    page_three = pages[2]
    page_three_fields = [
        element for element in page_three["elements"] if element["type"] == "field"
    ]

    print(f"PDF: {pdf_path}")
    print(f"Total pages: {structure['pages']}")
    print(f"Form technology: {structure['form_technology']}")
    print(f"Total form fields: {len(fields)}")
    print(f"Field type counts: {json.dumps(field_type_counts(structure), sort_keys=True)}")
    print(f"Fields on page 3: {len(page_three_fields)}")
    print("Page 3 dimensions: " + json.dumps({"width": page_three["width"], "height": page_three["height"]}))
    print("Page 3 fields:")
    print(json.dumps(page_three_fields[:5], indent=2))
    print("Representative text elements:")
    print(json.dumps([element for element in page_three["elements"] if element["type"] == "text"][:3], indent=2))
    print("Fields grouped by page (first five pages):")
    print(json.dumps({str(page["page"]): sum(element["type"] == "field" for element in page["elements"]) for page in pages[:5]}, indent=2))

    if not any("BHCK4435" in field["name"] for field in page_three_fields):
        raise AssertionError("Expected BHCK4435 on page 3")


if __name__ == "__main__":
    main()