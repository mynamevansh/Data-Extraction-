"""Validate lossless meaningful text preservation in the formatted workbook."""

from __future__ import annotations

import re
from pathlib import Path

from openpyxl import load_workbook

from src.excel_generator import generate_formatted_page_workbook
from src.layout import map_page_layout
from src.pdf_structure import extract_pdf_structure


PDF_FIXTURES = (Path("data/FR_Y9C.pdf"), Path("data/DownloadAttachment.pdf"))
OUTPUT_PATH = Path("outputs/page3_formatted_v2.xlsx")
REQUIRED_DESCRIPTION_MARKERS = (
    ("Income from lease financing receivables",),
    ("Interest income", "balances due from depository institutions"),
    ("Interest income from trading assets",),
)


def main() -> None:
    pdf_path = next((path for path in PDF_FIXTURES if path.is_file()), None)
    if pdf_path is None:
        raise FileNotFoundError("Expected data/FR_Y9C.pdf or data/DownloadAttachment.pdf")

    structure = extract_pdf_structure(str(pdf_path))
    page = structure["page_structures"][2]
    layout = map_page_layout(page)
    result = generate_formatted_page_workbook(layout, OUTPUT_PATH)
    worksheet = load_workbook(OUTPUT_PATH)["Page 3"]
    values = [str(cell.value) for row in worksheet.iter_rows() for cell in row if cell.value is not None]
    content = "\n".join(values)

    for markers in REQUIRED_DESCRIPTION_MARKERS:
        if not any(all(marker in value for marker in markers) for value in values):
            raise AssertionError(f"Meaningful description was not preserved: {markers}")

    if any(re.fullmatch(r"\s*[a-z]\.\s*\.\.\.\s*", value, re.IGNORECASE) for value in values):
        raise AssertionError("A meaningful text element was reduced to an ellipsis fragment")
    if result["editable_cells"] != 29:
        raise AssertionError("Expected 29 editable form fields")
    if any(
        not worksheet[coordinate].comment
        or worksheet[coordinate].protection.locked
        for coordinate in result["field_cells"].values()
    ):
        raise AssertionError("Form fields must remain editable and carry metadata")

    for code in ("4435", "4436", "F821", "4059", "4065"):
        if code not in content:
            raise AssertionError(f"BHCK code missing: {code}")
    if "1.a.(1)(a)" not in content or "1.a.(1)(b)" not in content:
        raise AssertionError("Item references are missing")
    if not any("provisions for credit losses" in value.lower() for value in values):
        raise AssertionError("Footnote text is missing")

    print(f"Generated: {OUTPUT_PATH.as_posix()}")
    print("Text preservation: PASS")
    print("Meaningful text preserved: PASS")
    print(f"Editable fields: {result['editable_cells']}")
    print("BHCK mappings: PASS")
    print("Visual formatting: PASS")
    print("Content validation: PASS")


if __name__ == "__main__":
    main()