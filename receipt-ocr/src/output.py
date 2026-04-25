from confidence import is_suspicious_value, normalize_confidence


def _normalize_value(value):
    if value is None:
        return ""
    return str(value)


def _build_field(value, confidence, field_name):
    normalized_value = _normalize_value(value)
    normalized_confidence = normalize_confidence(confidence)
    is_missing = normalized_value == ""
    if is_missing:
        normalized_confidence = 0.0
    elif is_suspicious_value(normalized_value, field_name):
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

