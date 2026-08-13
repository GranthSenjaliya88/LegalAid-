import hashlib
import json
from pathlib import Path


def sha256_text(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def validate_record(record: dict) -> list[str]:
    errors = []

    required = [
        "act_name",
        "section_number",
        "title",
        "full_text",
        "source",
    ]

    for field in required:
        if not record.get(field):
            errors.append(f"Missing field: {field}")

    source = record.get("source", {}) if isinstance(record.get("source"), dict) else {}

    if not source.get("authority"):
        errors.append("Missing source authority")

    if not source.get("official_url"):
        errors.append("Missing official URL")

    return errors


def load_record(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_file(path: Path) -> dict:
    record = load_record(path)

    errors = validate_record(record)

    return {
        "file": str(path),
        "valid": len(errors) == 0,
        "errors": errors,
        "content_hash": sha256_text(
            json.dumps(
                record,
                sort_keys=True,
                ensure_ascii=False,
            )
        ),
    }
