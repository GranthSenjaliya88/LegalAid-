"""
Fact Extractor Service (Phase 5 helper).
Extracts and validates structured facts while discarding sensitive user PII (Aadhaar, PAN, passwords).
"""

import re
from typing import Dict, Any
from app.schemas.case import CaseFactsData


SENSITIVE_PII_PATTERNS = [
    r"\b\d{4}\s?\d{4}\s?\d{4}\b",  # Aadhaar-like 12 digits
    r"\b[A-Z]{5}\d{4}[A-Z]{1}\b",  # PAN card pattern
    r"\bpass(?:word)?\s*[:=]\s*\S+", # Passwords
    r"\bcvv\s*[:=]\s*\d{3}\b",     # CVV
]


def sanitize_facts(facts_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize facts dict by scrubbing accidentally provided sensitive PII."""
    clean_dict = {}
    for key, val in facts_dict.items():
        if val is None:
            clean_dict[key] = None
            continue

        str_val = str(val)
        for pattern in SENSITIVE_PII_PATTERNS:
            str_val = re.sub(pattern, "[REDACTED_SENSITIVE_DATA]", str_val, flags=re.IGNORECASE)
        clean_dict[key] = str_val if isinstance(val, str) else val

    return clean_dict
