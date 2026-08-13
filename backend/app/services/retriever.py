"""
Retrieval Service (Phase 6).
Calls database corpus search engine directly.
Returns ranked matches or 'insufficient_confidence' status.
"""

from typing import Dict, Any, Optional
from app.legal.corpus_search import search_corpus
from app.schemas.legal import RetrievalResponseData


def retrieve_legal_sections(domain: Optional[str], facts: Dict[str, Any], limit: int = 5) -> RetrievalResponseData:
    """Execute legal corpus retrieval on SQLite/DB database."""
    return search_corpus(domain=domain, facts=facts, limit=limit)
