def _normalize_confidence(value):
    if value is None:
        return 0.0
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    numeric = max(0.0, min(1.0, numeric))
    if numeric < 0.3:
        numeric *= 0.5
    return round(numeric, 2)


def _normalize_value(value):
    if value is None:
        return ""
    return str(value)


def _is_suspicious_value(value: str, field_name: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return True
    if field_name == "store_name" and len(stripped) < 3:
        return True
    if field_name == "date" and len(stripped) < 8:
        return True
    if field_name == "total_amount" and len(stripped) < 4:
        return True
    return False


def _build_field(value, confidence, field_name):
    normalized_value = _normalize_value(value)
    normalized_confidence = _normalize_confidence(confidence)
    is_missing = normalized_value == ""
    if is_missing:
        normalized_confidence = 0.0
    elif _is_suspicious_value(normalized_value, field_name):
        normalized_confidence = round(normalized_confidence * 0.5, 2)

    field = {
        "value": normalized_value,
        "confidence": normalized_confidence,
    }

    if is_missing or normalized_confidence < 0.7:
        field["low_confidence"] = True

    return field


def build_output(
    store_name,
    store_confidence,
    date,
    date_confidence,
    total_amount,
    total_confidence,
):
    return {
        "store_name": _build_field(store_name, store_confidence, "store_name"),
        "date": _build_field(date, date_confidence, "date"),
        "total_amount": _build_field(total_amount, total_confidence, "total_amount"),
    }

