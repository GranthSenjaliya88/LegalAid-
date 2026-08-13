"""
Security utilities: prompt injection defense, input validation, and sanitization.
"""
import re
from fastapi import HTTPException, status

MAX_TEXT_LENGTH = 8000
UNSUPPORTED_LANGUAGES = ["zh", "ru", "ar", "es", "fr", "de", "ja"]

# Common prompt injection patterns trying to overwrite LLM instructions
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous\s+)?instructions",
    r"disregard\s+(all\s+)?(previous\s+)?instructions",
    r"forget\s+(all\s+)?(previous\s+)?instructions",
    r"you\s+are\s+now\s+a",
    r"system\s+prompt",
    r"override\s+system",
    r"tell\s+me\s+section\s+\d+",
    r"invent\s+a\s+law",
    r"make\s+up\s+a\s+section",
]


def sanitize_input(text: str, language: str = "en") -> str:
    """
    Validate and sanitize user input text.
    Raises HTTPException for malicious, empty, or oversized input.
    """
    if not text or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input text cannot be empty."
        )

    text = text.strip()
    if len(text) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Input text exceeds maximum allowed length of {MAX_TEXT_LENGTH} characters."
        )

    if language.lower() in UNSUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language '{language}' is not supported. Supported languages: English (en), Hindi (hi)."
        )

    # Redact sensitive credentials (Aadhaar, PAN, 16-digit card numbers, Passwords, OTPs)
    text = re.sub(r"\b[2-9]{1}\d{3}\s?\d{4}\s?\d{4}\b", "[REDACTED AADHAAR]", text)  # Aadhaar 12-digit
    text = re.sub(r"\b[A-Z]{5}\d{4}[A-Z]{1}\b", "[REDACTED PAN]", text, flags=re.IGNORECASE)  # PAN 10-char
    text = re.sub(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[REDACTED CARD NUMBER]", text)  # 16-digit Card
    text = re.sub(r"(?i)\b(password|pin|otp|cvv)\s*[:=]\s*\S+", r"\1: [REDACTED SENSITIVE INFO]", text)

    return text


def sanitize_for_prompt(text: str) -> str:
    """
    Sanitize input text before including it into LLM prompt templates.
    Wraps text clearly as user DATA and escapes delimiter characters.
    """
    # Replace backticks or quotes that try to break format
    clean = text.replace("```", "'''")
    
    # Strip prompt injection phrases or flag them
    for pattern in PROMPT_INJECTION_PATTERNS:
        clean = re.sub(pattern, "[FILTERED_INSTRUCTION]", clean, flags=re.IGNORECASE)

    return clean
