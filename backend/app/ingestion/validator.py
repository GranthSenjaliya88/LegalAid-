"""
Ingestion Data Quality Validator Module.
"""

from typing import Dict, Any, Tuple, List
from app.legal.ingestion_pipeline import run_data_quality_checks


def validate_legal_record(record: Dict[str, Any], record_type: str = "STATUTE") -> Tuple[str, List[str]]:
    """Validate incoming record against quality gate standards."""
    return run_data_quality_checks(record, record_type)
