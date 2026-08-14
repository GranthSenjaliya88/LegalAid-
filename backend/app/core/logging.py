"""
Logging configuration with privacy protection (redacting PII and sensitive data).
"""
import logging
import re
import sys


class PrivacyFilter(logging.Filter):
    """Mask credentials and sensitive user data from logs (Part 30).

    Never log: OTP, password, PIN, bank password, or full payment credentials.
    This filter redacts API keys, masks values that follow a sensitive keyword
    (password/otp/pin/cvv/token/secret/…), and masks long digit runs that look
    like card or account numbers.
    """

    # key: value  /  key=value  /  "key": "value"  where key is sensitive.
    _KEYED = re.compile(
        r"(?i)\b(password|passwd|pwd|otp|pin|cvv|cvc|secret|token|api[_-]?key|"
        r"authorization|auth|bank[_\s-]?password|card[_\s-]?number|account[_\s-]?number)\b"
        r"\s*[:=]\s*[\"']?[^\s\"',}]+"
    )
    # 12–19 digit runs (payment cards / long account numbers), allowing spaces/dashes.
    _LONG_DIGITS = re.compile(r"\b(?:\d[ -]?){12,19}\b")

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
        except Exception:
            return True
        if not isinstance(msg, str):
            return True
        if any(k in msg for k in ["API_KEY", "SECRET_KEY"]):
            record.msg, record.args = "[LOG REDACTED: SENSITIVE KEY MENTIONED]", None
            return True
        redacted = self._KEYED.sub(
            lambda m: f"{m.group(1)}: [REDACTED]", msg
        )
        redacted = self._LONG_DIGITS.sub("[REDACTED]", redacted)
        if redacted != msg:
            record.msg, record.args = redacted, None
        return True


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("legalaid")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        handler.addFilter(PrivacyFilter())
        logger.addHandler(handler)

    return logger


logger = setup_logging()
