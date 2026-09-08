"""Diagnostic for mapping one native PDF page into logical grid positions."""

from __future__ import annotations

import json
from pathlib import Path

from src.layout import map_page_layout
from src.pdf_structure import extract_pdf_structure


PDF_FIXTURES = (Path("data/FR_Y9C.pdf"), Path("data/DownloadAttachment.pdf"))


def main() -> None:
    pdf_path = next((path for path in PDF_FIXTURES if path.is_file()), None)
    if pdf_path is None:
        raise FileNotFoundError("Expected data/FR_Y9C.pdf or data/DownloadAttachment.pdf")

    structure = extract_pdf_structure(str(pdf_path))
    layout = map_page_layout(structure["page_structures"][2])
    fields = [element for element in layout["elements"] if element["type"] == "field"]
    texts = [element for element in layout["elements"] if element["type"] == "text"]

    print(f"PDF Page: {layout['page']}")
    print(f"PDF Dimensions: {layout['page_width']} x {layout['page_height']}")
    print(f"Detected logical rows: {layout['logical_rows']}")
    print(f"Detected logical columns: {layout['logical_columns']}")
    print(f"Row tolerance: {layout['row_tolerance']:.6f} normalized")
    print(f"Column tolerance: {layout['column_tolerance']:.6f} normalized")
    print(f"Mapped text elements: {len(texts)}")
    print(f"Mapped form fields: {len(fields)}")

    for row in sorted(set(element["excel_row"] for element in layout["elements"])):
        print(f"\nRow {row}:")
        for element in [item for item in layout["elements"] if item["excel_row"] == row]:
            label = element["text"] if element["type"] == "text" else element["name"]
            print(
                f"  {element['type'].upper()}: {label!r}\n"
                f"    PDF bbox: {element['bbox']}\n"
                f"    Excel position: row={element['excel_row']}, col={element['excel_col']}"
            )

    sample = next((element for element in fields if "BHCK4435" in element["name"]), None)
    if sample is None:
        raise AssertionError("Expected BHCK4435 in the page-3 mapping")

    expected_fields = ("BHCK4435", "BHCK4436", "BHCKF821", "BHCK4059", "BHCK4065")
    mapped_fields = [
        next(element for element in fields if field_name in element["name"])
        for field_name in expected_fields
    ]
    mapped_rows = [element["excel_row"] for element in mapped_fields]
    if len(set(mapped_rows)) != len(mapped_rows) or mapped_rows != sorted(mapped_rows):
        raise AssertionError(
            f"Expected increasing, distinct rows for {expected_fields}: {mapped_rows}"
        )

    mapped_y = [element["bbox"][1] for element in mapped_fields]
    if mapped_y != sorted(mapped_y):
        raise AssertionError(f"Expected field Y ordering to be preserved: {mapped_y}")

    print("\nCorrected BHCK field mappings:")
    for element in mapped_fields:
        print(
            f"  {element['name']}: y={element['bbox'][1]}, "
            f"row={element['excel_row']}, col={element['excel_col']}"
        )
    print("\nSample BHCK4435 mapping:")
    print(json.dumps(sample, indent=2))


if __name__ == "__main__":
    main()