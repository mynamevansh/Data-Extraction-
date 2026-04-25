# Receipt OCR System

A Python-based OCR pipeline that extracts structured information from receipt images and exports machine-readable JSON outputs.  
The system combines OCR text recognition with rule-based extraction logic to identify key fields such as store name, date, and total amount, while attaching confidence signals for reliability in real-world use.

## Features

- Extracts structured receipt fields: `store_name`, `date`, and `total_amount`
- Supports batch processing for all images in `data/`
- Supports single-image processing via CLI argument
- Generates one JSON file per receipt in `outputs/`
- Includes confidence scoring and low-confidence flags
- Handles noisy OCR text with validation and fallback logic
- Builds an expense summary (`summary.json`) from processed outputs

## Folder Structure

```text
receipt-ocr/
│── data/                  # Input receipt images
│── outputs/               # Generated JSON outputs
│── src/
│   ├── main.py
│   ├── ocr.py
│   ├── extract.py
│   ├── output.py
│   ├── preprocess.py
│   └── confidence.py
│── README.md
│── requirements.txt
```

## How to Run the Project

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Process all images in `data/`

```bash
python src/main.py
```

### 3) Process a specific image

```bash
python src/main.py receipt3.jpg
```

### 4) Reprocess even if output already exists

```bash
python src/main.py --force
```

### 5) Run basic validation tests

```bash
python test.py
```

## Example Output (JSON)

```json
{
  "store_name": {
    "value": "SATU KAMPUNG ENTERPRISE",
    "confidence": 1.0
  },
  "date": {
    "value": "2021-10-13",
    "confidence": 0.3,
    "low_confidence": true
  },
  "total_amount": {
    "value": "63.00",
    "confidence": 0.59,
    "low_confidence": true
  }
}
```

## Approach

1. OCR reads receipt images and returns text with confidence values.
2. Rule-based extraction identifies target fields:
   - keyword-driven matching for totals and dates
   - regex normalization for amounts and date formats
   - candidate scoring to select best field matches
3. Output shaping normalizes values, applies confidence handling, and marks low-confidence fields.
4. Results are saved as per-receipt JSON files for downstream use.

## Tools & Technologies Used

- Python
- EasyOCR
- Regular Expressions (regex)
- JSON for structured outputs
- Pathlib and standard Python file I/O

## Challenges Faced

- OCR noise (misread characters like `O` vs `0`)
- Multiple competing amount fields (subtotal, total, tax-inclusive lines)
- Inconsistent date formats across different receipts
- Variable layout quality, skew, and text density in real-world images

## Edge Case Handling

- Missing fields default to safe values and are marked low confidence
- Invalid totals are ignored unless they pass numeric validation
- If total is missing, fallback value `0.00` is used
- Empty OCR extraction for a file is safely skipped
- Already processed files are skipped to avoid duplicate overwrites

## Improvements / Future Work

- Add stronger preprocessing for blur, skew, and low-light images
- Introduce layout-aware extraction for complex receipt templates
- Improve confidence calibration with learned models
- Add test suite with benchmark receipts and expected outputs
- Provide optional API or dashboard layer for integrations

## Summary

The Receipt OCR System provides a practical, production-leaning pipeline for extracting structured data from noisy receipt images, with confidence-aware outputs and robust handling of common OCR edge cases.

