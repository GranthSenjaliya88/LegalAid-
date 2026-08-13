"""
Importer Module for LegalAId Corpus Ingestion.
"""

import sqlite3
from pathlib import Path
from typing import Tuple, Optional, Dict
from app.legal.ingestion_pipeline import (
    ingest_rules_and_regulations,
    ingest_notifications,
    ingest_authorities_and_procedures,
    ingest_judgments,
    ingest_legal_concepts
)


def import_all_corpus_data(conn: sqlite3.Connection, data_dir: Optional[Path] = None) -> Dict[str, int]:
    """Import all statutory, procedural, and judicial corpus datasets."""
    auth_cnt, proc_cnt = ingest_authorities_and_procedures(conn)
    concepts_cnt = ingest_legal_concepts(conn)
    rules_cnt, regs_cnt = ingest_rules_and_regulations(conn)
    notif_cnt = ingest_notifications(conn)
    judg_cnt = ingest_judgments(conn)

    return {
        "authorities": auth_cnt,
        "procedures": proc_cnt,
        "concepts": concepts_cnt,
        "rules": rules_cnt,
        "regulations": regs_cnt,
        "notifications": notif_cnt,
        "judgments": judg_cnt
    }
