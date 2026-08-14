"""
Ingestion Package for LegalAId.
"""
from app.legal.ingestion_pipeline import (
    run_data_quality_checks,
    ingest_rules_and_regulations,
    ingest_notifications,
    ingest_authorities_and_procedures,
    ingest_judgments,
    ingest_legal_concepts
)
