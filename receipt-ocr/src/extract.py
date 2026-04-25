import re
from datetime import datetime

TOTAL_KEYWORDS = (
    ("inclusive", 6),
    ("grand total", 5),
    ("total sales", 4),
    ("amount", 3),
    ("total", 2),
)


def clean_amount(text):
    text = str(text)
    text = text.replace(" ", "")
    text = text.replace(",", ".")
    text = text.replace("O", "0").replace("o", "0")
    text = text.replace("u", "0")
    text = re.sub(r"[^\d.]", "", text)
    return text


def normalize_total_value(value):
    cleaned = clean_amount(str(value))
    if not re.fullmatch(r"\d+(?:\.\d{1,2})?", cleaned):
        return None
    return f"{float(cleaned):.2f}"


def _keyword_score(text: str) -> int:
    lowered = text.lower()
    for keyword, score in TOTAL_KEYWORDS:
        if keyword in lowered:
            return score
    return 0


def _extract_numeric_candidates(text: str) -> list[str]:
    matches = re.findall(r"(?:\d[\dOou,\.\s]{0,}\d|\d)", text)
    values: list[str] = []
    for match in matches:
        normalized = normalize_total_value(match)
        if normalized is not None:
            values.append(normalized)
    return values


def extract_total(texts):
    best_match = None
    best_priority = -1
    best_confidence = 0.0

    for i, t in enumerate(texts):
        line_text = str(t.get("text", ""))
        score = _keyword_score(line_text)

        if score > 0:
            numbers = _extract_numeric_candidates(line_text)
            conf = float(t.get("confidence", 0.0))

            if not numbers and i + 1 < len(texts):
                next_text = str(texts[i + 1].get("text", ""))
                numbers = _extract_numeric_candidates(next_text)
                conf = float(texts[i + 1].get("confidence", 0.0))

            if numbers:
                value = numbers[-1]
                if score > best_priority or (
                    score == best_priority and conf > best_confidence
                ):
                    best_priority = score
                    best_confidence = conf
                    best_match = (value, conf)

    return best_match if best_match else (None, 0.0)


def extract_store_name(texts):
    ignored_words = {"POSTED", "TEL"}
    candidates = []

    for item in texts[:5]:
        raw_text = str(item.get("text", "")).strip()
        if not raw_text:
            continue

        upper_text = raw_text.upper()
        if upper_text in ignored_words:
            continue

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


def _clean_date_text(text):
    replacements = {
        "O": "0",
        "o": "0",
        "I": "1",
        "l": "1",
        "|": "1",
        "S": "5",
        "s": "5",
        "B": "8",
    }
    cleaned_chars = []
    for ch in text:
        cleaned_chars.append(replacements.get(ch, ch))
    return "".join(cleaned_chars)


def _to_iso_date(day, month, year):
    day = int(day)
    month = int(month)
    year = int(year)
    if year < 100:
        year += 2000
    try:
        parsed = datetime(year, month, day)
    except ValueError:
        return None
    return parsed.strftime("%Y-%m-%d")


def normalize_date_from_8digits(s):
    if len(s) != 8 or not s.isdigit():
        return None

    dd, mm, yyyy = s[:2], s[2:4], s[4:]

    if int(yyyy) < 1900:
        yyyy = "20" + yyyy[-2:]

    if 1 <= int(dd) <= 31 and 1 <= int(mm) <= 12:
        return f"{yyyy}-{mm.zfill(2)}-{dd.zfill(2)}"

    return None


def _extract_date_from_line(text):
    cleaned = _clean_date_text(text)

    for match in re.finditer(r"\b(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{2,4})\b", cleaned):
        iso = _to_iso_date(match.group(1), match.group(2), match.group(3))
        if iso:
            return iso

    for match in re.finditer(r"\b(\d{8})\b", cleaned):
        iso = normalize_date_from_8digits(match.group(1))
        if iso:
            return iso
    for match in re.finditer(r"\b(\d{2})(\d{2})(\d{2})\b", cleaned):
        iso = _to_iso_date(match.group(1), match.group(2), match.group(3))
        if iso:
            return iso

    return None


def extract_date(texts):
    keywords = ("date", "dale", "invoice")
    best = None
    best_score = -1.0

    for i, item in enumerate(texts):
        line = str(item.get("text", ""))
        line_lower = line.lower()
        conf = float(item.get("confidence", 0.0))

        if any(k in line_lower for k in keywords):
            nearby = [item]
            if i + 1 < len(texts):
                nearby.append(texts[i + 1])

            for cand in nearby:
                cand_line = str(cand.get("text", ""))
                cand_conf = float(cand.get("confidence", 0.0))
                iso = _extract_date_from_line(cand_line)
                if iso:
                    score = cand_conf + 1.0
                    if score > best_score:
                        best_score = score
                        best = (iso, cand_conf)

    if best is None:
        for item in texts:
            line = str(item.get("text", ""))
            conf = float(item.get("confidence", 0.0))
            iso = _extract_date_from_line(line)
            if iso and conf > best_score:
                best_score = conf
                best = (iso, conf)

    return best if best else (None, 0.0)
