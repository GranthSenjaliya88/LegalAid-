"""Text processing helper functions."""

import re


def clean_whitespace(text: str) -> str:
    """Normalize whitespace and newlines."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def truncate_text(text: str, max_chars: int = 200) -> str:
    """Truncate text cleanly with ellipsis."""
    if not text or len(text) <= max_chars:
        return text or ""
    return text[:max_chars].rsplit(" ", 1)[0] + "…"
