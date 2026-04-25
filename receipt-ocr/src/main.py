import json
import sys
from pathlib import Path

from extract import extract_date, extract_store_name, extract_total
from ocr import extract_text
from output import build_output

DEBUG = False


def print_debug_logs(texts: list[dict[str, float | str]]) -> None:
    for item in texts:
        print(f'Text: {item["text"]} | Confidence: {item["confidence"]:.2f}')


def process_image(image_path: str) -> dict[str, dict[str, float | str | bool]] | None:
    texts = extract_text(image_path)
    if not texts:
        return None
    if DEBUG:
        print_debug_logs(texts)

    store, store_conf = extract_store_name(texts)
    date, date_conf = extract_date(texts)
    total, total_conf = extract_total(texts)
    if total is None:
        total = "0.00"
        total_conf = 0.0

    return build_output(
        store,
        store_conf,
        date,
        date_conf,
        total,
        total_conf,
    )


def to_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def generate_expense_summary(output_folder: str = "outputs") -> dict[str, float | int]:
    output_path = Path(output_folder)
    json_files = sorted(
        path
        for path in output_path.glob("*.json")
        if path.is_file() and path.name != "summary.json"
    )

    total_spent = 0.0
    confidence_sum = 0.0
    low_confidence_receipts = 0

    for file_path in json_files:
        try:
            with file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            continue

        total_amount = data.get("total_amount", {})
        total_spent += to_float(total_amount.get("value"))
        confidence_sum += to_float(total_amount.get("confidence"))
        if bool(total_amount.get("low_confidence")):
            low_confidence_receipts += 1

    total_receipts = len(json_files)
    average_confidence = (
        round(confidence_sum / total_receipts, 2) if total_receipts > 0 else 0.0
    )
    summary = {
        "total_receipts": total_receipts,
        "total_spent": round(total_spent, 2),
        "average_confidence": average_confidence,
        "low_confidence_receipts": low_confidence_receipts,
    }

    summary_file = output_path / "summary.json"
    with summary_file.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    print("Expense summary:")
    print(json.dumps(summary, indent=2))
    print(f"Saved to {summary_file.as_posix()}")
    return summary


def process_folder(input_folder: str = "data", output_folder: str = "outputs") -> None:
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1:
        image_files = [input_path / sys.argv[1]]
    else:
        image_files = sorted(
            path
            for path in input_path.iterdir()
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png"}
        )

    for image_path in image_files:
        try:
            if image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                print(f"Failed to process {image_path.name}: unsupported file type")
                continue

            output_file = output_path / f"{image_path.stem}.json"
            if output_file.exists():
                print(f"Skipping {image_path.name} (already processed)")
                continue

            print(f"Processing {image_path.name}...")
            final_output = process_image(str(image_path))
            if final_output is None:
                print(f"Failed to process {image_path.name}: no text extracted")
                continue
            with output_file.open("w", encoding="utf-8") as file:
                json.dump(final_output, file, indent=2)

            print(f"Saved to {output_file.as_posix()}")
        except Exception as error:
            print(f"Failed to process {image_path.name}: {error}")


def main() -> None:
    process_folder("data", "outputs")
    generate_expense_summary("outputs")


if __name__ == "__main__":
    main()

