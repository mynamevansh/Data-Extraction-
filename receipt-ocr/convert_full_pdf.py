"""Convert the complete FR Y-9C PDF into an editable Excel workbook."""

from __future__ import annotations

import json
from pathlib import Path

from src.excel_generator import generate_full_workbook
from src.pdf_structure import extract_pdf_structure


PDF_PATH = Path("data/DownloadAttachment.pdf")
OUTPUT_PATH = Path("outputs/FR_Y9C_converted.xlsx")
REPORT_PATH = Path("outputs/conversion_report.json")


def main() -> None:
    structure = extract_pdf_structure(str(PDF_PATH))
    result = generate_full_workbook(structure, OUTPUT_PATH)
    report = {
        "pdf_pages": result["pdf_pages"],
        "pdf_form_fields": sum(
            1
            for page in structure["page_structures"]
            for element in page["elements"]
            if element["type"] == "field"
        ),
        "excel_form_fields": result["excel_form_fields"],
        "unsupported_fields": result["unsupported_fields"],
        "failed_pages": result["failed_pages"],
        "pages": result["pages"],
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("========================================")
    print("FR Y-9C FULL CONVERSION")
    print("========================================")
    print(f"PDF pages: {report['pdf_pages']}")
    print(f"Excel worksheets: {result['excel_worksheets']}")
    print(f"PDF form fields: {report['pdf_form_fields']}")
    print(f"Excel editable fields: {report['excel_form_fields']}")
    print(f"Unsupported fields: {len(report['unsupported_fields'])}")
    print(f"Pages converted successfully: {report['pdf_pages'] - len(report['failed_pages'])}")
    print(f"Pages failed: {len(report['failed_pages'])}")
    print("Page 3 validation: PASS" if "3" in report["pages"] and "error" not in report["pages"]["3"] else "Page 3 validation: FAIL")
    print("Field accounting: PASS" if report["pdf_form_fields"] == report["excel_form_fields"] else "Field accounting: FAIL")
    print("Workbook validation: PASS" if not report["failed_pages"] else "Workbook validation: FAIL")
    print(f"\nGenerated:\n{OUTPUT_PATH.as_posix()}")
    print(f"\nReport:\n{REPORT_PATH.as_posix()}")


if __name__ == "__main__":
    main()