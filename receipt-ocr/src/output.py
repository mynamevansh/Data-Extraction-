"""
Build final structured output for receipt OCR fields.
"""


def _normalize_confidence(value):
    """Return a safe, rounded confidence float."""
    if value is None:
        return 0.0
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    return round(numeric, 2)


def _normalize_value(value):
    """Return a safe string value."""
    if value is None:
        return ""
    return str(value)


def _build_field(value, confidence):
    """Build one structured field block."""
    normalized_value = _normalize_value(value)
    normalized_confidence = _normalize_confidence(confidence)

    field = {
        "value": normalized_value,
        "confidence": normalized_confidence,
    }

    if normalized_confidence < 0.7:
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
    """Build final receipt output dictionary."""
    return {
        "store_name": _build_field(store_name, store_confidence),
        "date": _build_field(date, date_confidence),
        "total_amount": _build_field(total_amount, total_confidence),
    }

