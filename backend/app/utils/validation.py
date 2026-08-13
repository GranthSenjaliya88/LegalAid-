"""Validation helpers for API endpoints."""

import uuid


def is_valid_uuid(val: str) -> bool:
    """Validate if string is a valid UUID."""
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
