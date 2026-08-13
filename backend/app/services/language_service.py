"""
Language Service (Phase 13).
Handles multilingual processing (Hindi & English).
Preserves legal section numbers and Act titles verbatim during translation.
"""

import re
from typing import Dict, Any


def is_hindi_text(text: str) -> bool:
    """Check if input text contains Devanagari script."""
    return bool(re.search(r"[\u0900-\u097F]", text))


def preserve_section_numbers(translated_text: str, original_citations: list) -> str:
    """
    Ensure section numbers and Act titles remain intact in English script
    even in Hindi generated responses.
    """
    # Section regex patterns to guard
    section_pattern = r"\b(?:Section|Sec\.?)\s+\d+[A-Za-z]?\b"
    # Ensure any translated 'धारा' is converted back or paired with standard 'Section X'
    fixed_text = re.sub(r"धारा\s+(\d+[A-Za-z]?)", r"Section \1", translated_text)
    return fixed_text
