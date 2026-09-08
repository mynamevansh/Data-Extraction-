from __future__ import annotations

import json
import re
from pathlib import Path

from src.main import generate_expense_summary, process_image
from src.ocr import extract_text
from src.pdf import extract_pdf, get_pdf_page_count

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PDF_FIXTURES = (
    Path("data/DownloadAttachment.pdf"),
    Path("Receipt_OCR_Assignment_Vansh_Final.pdf"),
)


def run_pdf_tests() -> bool:
    pdf_fixture = next((path for path in PDF_FIXTURES if path.is_file()), None)
    if pdf_fixture is None:
        print("PDF Test Skipped: no PDF fixture found")
        return True

    page_count = get_pdf_page_count(str(pdf_fixture))
    print(f"PDF pages: {page_count}")
    if page_count < 1:
        print("PDF Test Failed: PDF has no pages")
        return False

    pages = extract_pdf(str(pdf_fixture), pages=[1])
    if not pages or pages[0]["page"] != 1:
        print("PDF Test Failed: page 1 was not extracted")
        return False

    print("PDF page 1 elements:")
    print(json.dumps(pages[0]["elements"][:3], indent=2))
    for element in pages[0]["elements"]:
        if not element["text"].strip() or element["source"] not in {"native_pdf", "ocr"}:
            print("PDF Test Failed: invalid extracted element")
            return False
        bbox = element["bbox"]
        if not bbox or not all(
            isinstance(coordinate, (int, float))
            for coordinate in (bbox if isinstance(bbox[0], (int, float)) else [value for point in bbox for value in point])
        ):
            print("PDF Test Failed: invalid element coordinates")
            return False
    return True


def run_basic_tests() -> bool:
    data_dir = Path("data")
    sample_images = sorted(
        path
        for path in data_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )[:3]

    if len(sample_images) < 2:
        print("Test Failed: need at least 2 sample images in data/")
        return False

    if not run_pdf_tests():
        return False

    ocr_results = extract_text(str(sample_images[0]))
    if not ocr_results:
        print(f"Test Failed: no OCR text for {sample_images[0].name}")
        return False

    for item in ocr_results:
        if not str(item.get("text", "")).strip():
            print("Test Failed: OCR result has empty text")
            return False
        if not isinstance(item.get("confidence"), float):
            print("Test Failed: OCR result has no numeric confidence")
            return False

        bbox = item.get("bbox")
        if not isinstance(bbox, list) or len(bbox) != 4:
            print("Test Failed: OCR result has an invalid bounding box")
            return False
        if any(
            not isinstance(point, list)
            or len(point) != 2
            or not all(isinstance(coordinate, (int, float)) for coordinate in point)
            for point in bbox
        ):
            print("Test Failed: OCR bounding box contains invalid coordinates")
            return False

    print("Representative OCR output:")
    print(json.dumps(ocr_results[:1], indent=2))

    for image_path in sample_images:
        result = process_image(str(image_path))
        if result is None:
            print(f"Test Failed: no OCR text for {image_path.name}")
            return False

        store_value = str(result.get("store_name", {}).get("value", "")).strip()
        total_value = str(result.get("total_amount", {}).get("value", "")).strip()
        date_value = str(result.get("date", {}).get("value", "")).strip()

        if not store_value:
            print(f"Test Failed: empty store_name for {image_path.name}")
            return False
        if not total_value:
            print(f"Test Failed: empty total_amount for {image_path.name}")
            return False
        try:
            numeric_total = float(total_value)
        except ValueError:
            print(f"Test Failed: non-numeric total_amount for {image_path.name}")
            return False
        if numeric_total < 0:
            print(f"Test Failed: negative total_amount for {image_path.name}")
            return False
        if date_value and not DATE_PATTERN.fullmatch(date_value):
            print(f"Test Failed: invalid date format for {image_path.name}")
            return False

    summary = generate_expense_summary("outputs")
    required_summary_keys = {
        "total_receipts",
        "total_spent",
        "average_confidence",
        "low_confidence_receipts",
    }
    if set(summary.keys()) != required_summary_keys:
        print("Test Failed: summary keys are incomplete")
        return False

    print("Test Passed")
    return True


if __name__ == "__main__":
    run_basic_tests()
