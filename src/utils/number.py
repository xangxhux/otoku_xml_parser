from typing import Optional


def to_int(value: Optional[str]) -> Optional[int]:
    """Convert a string to int, returning None for None, empty, or non-numeric values."""
    if value is None or not value.strip():
        return None
    try:
        return int(value.strip())
    except (ValueError, TypeError):
        return None
