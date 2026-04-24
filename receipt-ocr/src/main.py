"""
Main entry point for the receipt OCR pipeline.
"""

from extract import extract_store_name, extract_total
from ocr import extract_text


def main() -> None:
    sample_image_path = "data/sample_receipt.jpg"

    try:
        texts = extract_text(sample_image_path)
        for item in texts:
            print(f'Text: {item["text"]} | Confidence: {item["confidence"]:.2f}')

        total, conf = extract_total(texts)
        print("Total:", total, "Confidence:", conf)

        store, conf = extract_store_name(texts)
        print("Store:", store, "Confidence:", conf)
    except FileNotFoundError as error:
        print(error)
    except Exception as error:
        print(f"OCR failed: {error}")


if __name__ == "__main__":
    main()

