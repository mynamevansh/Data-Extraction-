"""
Field extraction logic for parsed OCR text.
"""

import re


def clean_amount(text):
    # fix OCR mistakes
    text = text.replace(" ", ".")
    text = text.replace("O", "0").replace("o", "0")
    text = text.replace("u", "0")
    return text


def extract_total(texts):
    best_match = None
    best_score = 0

    for i, t in enumerate(texts):
        text = t["text"].lower()

        score = 0

        # scoring logic
        if "inclusive" in text:
            score = 5
        elif "grand total" in text:
            score = 4
        elif "total sales" in text:
            score = 3
        elif "total" in text:
            score = 1

        if score > 0:
            # try extracting number
            numbers = re.findall(r"\d+[\.\s]?\d*", t["text"])

            if not numbers and i + 1 < len(texts):
                numbers = re.findall(r"\d+[\.\s]?\d*", texts[i + 1]["text"])
                conf = texts[i + 1]["confidence"]
            else:
                conf = t["confidence"]

            if numbers:
                value = clean_amount(numbers[-1])

                if score > best_score:
                    best_score = score
                    best_match = (value, conf)

    return best_match if best_match else (None, 0.0)


def extract_store_name(texts):
    """Extract store name from first OCR lines using confidence and uppercase preference."""
    ignored_words = {"POSTED", "TEL"}
    candidates = []

    for item in texts[:5]:
        raw_text = str(item.get("text", "")).strip()
        if not raw_text:
            continue

        upper_text = raw_text.upper()
        if upper_text in ignored_words:
            continue

        # Skip very short labels/noise.
        if len(raw_text) < 3:
            continue

        confidence = float(item.get("confidence", 0.0))
        uppercase_bonus = 0.1 if raw_text.isupper() else 0.0
        score = confidence + uppercase_bonus
        candidates.append((score, raw_text, confidence))

    if not candidates:
        return None, 0.0

    _, best_text, best_conf = max(candidates, key=lambda x: x[0])
    return best_text, best_conf
