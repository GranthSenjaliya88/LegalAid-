"""
Hybrid Search Fusion Module.
Combines BM25 FTS5, FAISS Dense Vector Cosine Similarity, Jurisdiction Ranking, and Currency Status Filters.
"""

from typing import Dict, Any, Optional
from app.legal.corpus_search import search_corpus
from app.schemas.legal import RetrievalResponseData


def execute_hybrid_retrieval(
    domain: Optional[str],
    facts: Dict[str, Any],
    limit: int = 10
) -> RetrievalResponseData:
    """Execute complete hybrid retrieval pipeline."""
    return search_corpus(domain=domain, facts=facts, limit=limit)
