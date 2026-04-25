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


def process_image(image_path: str) -> dict[str, dict[str, float | str | bool]]:
    texts = extract_text(image_path)
    if DEBUG:
        print_debug_logs(texts)

    store, store_conf = extract_store_name(texts)
    date, date_conf = extract_date(texts)
    total, total_conf = extract_total(texts)

    return build_output(
        store,
        store_conf,
        date,
        date_conf,
        total,
        total_conf,
    )


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
            with output_file.open("w", encoding="utf-8") as file:
                json.dump(final_output, file, indent=2)

            print(f"Saved to {output_file.as_posix()}")
        except Exception as error:
            print(f"Failed to process {image_path.name}: {error}")


def main() -> None:
    process_folder("data", "outputs")


if __name__ == "__main__":
    main()

