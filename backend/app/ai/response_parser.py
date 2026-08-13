"""
JSON extraction and schema validation helpers for AI responses.
"""
import json
import re
from typing import Dict, Any, Optional
from app.core.logging import logger


def parse_json_response(raw_text: str) -> Optional[Dict[str, Any]]:
    """Clean markdown code fences and parse JSON string."""
    if not raw_text or not raw_text.strip():
        return None

    clean = raw_text.strip()
    clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s*```$", "", clean)

    # Search for first '{' and last '}'
    start_idx = clean.find("{")
    end_idx = clean.rfind("}")

    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        clean = clean[start_idx : end_idx + 1]

    try:
        return json.loads(clean)
    except json.JSONDecodeError as exc:
        logger.warning("Failed to parse JSON response from LLM: %s", exc)
        return None
