from __future__ import annotations

import sys
import re
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from main import generate_expense_summary, process_image  # noqa: E402

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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
