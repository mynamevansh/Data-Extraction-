def normalize_confidence(value) -> float:
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


def is_suspicious_value(value: str, field_name: str) -> bool:
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
