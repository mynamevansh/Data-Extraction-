"""
Main entry point for the receipt OCR pipeline.
"""

from extract import extract_date, extract_store_name, extract_total
from ocr import extract_text
from output import build_output


def main() -> None:
    sample_image_path = "data/sample_receipt.jpg"

    try:
        texts = extract_text(sample_image_path)
        for item in texts:
            print(f'Text: {item["text"]} | Confidence: {item["confidence"]:.2f}')

        store, store_conf = extract_store_name(texts)
        date, date_conf = extract_date(texts)
        total, total_conf = extract_total(texts)

        final_output = build_output(
            store,
            store_conf,
            date,
            date_conf,
            total,
            total_conf,
        )
        print(final_output)
    except FileNotFoundError as error:
        print(error)
    except Exception as error:
        print(f"OCR failed: {error}")


if __name__ == "__main__":
    main()

