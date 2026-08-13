"""
BM25 FTS5 Search Module.
"""

import sqlite3
from typing import List, Dict, Any, Optional
from app.legal.corpus_search import _query_fts, _query_like_fallback


def search_bm25_fts(
    conn: sqlite3.Connection,
    fts_query: str,
    query_words: List[str],
    domain: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 10
):
    """Execute BM25 FTS5 search query."""
    return _query_fts(conn, fts_query=fts_query, query_words=query_words, domain=domain, state=state, limit=limit)
