"""
FTS5 & Vector Store Indexer Module.
"""

from pathlib import Path
from rebuild_fts import rebuild_fts
from app.db.database import DB_PATH


def sync_all_indexes(db_path: Path = DB_PATH) -> int:
    """Rebuild FTS5 and sync indexes."""
    return rebuild_fts(db_path)
