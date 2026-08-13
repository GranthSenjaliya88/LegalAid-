"""
Test suite for FTS5, Vector Search, and Hybrid Retrieval Engine.
"""

from app.db.database import get_connection
from app.legal.corpus_search import search_corpus


def test_hybrid_retrieval_execution():
    """Verify hybrid search executes and returns relevant verified matches."""
    result = search_corpus(
        domain="tenant",
        facts={"incident": "landlord refused security deposit", "state": "Karnataka", "city": "Bengaluru"}
    )
    assert result.status != "error"
    assert len(result.matches) > 0
    assert any("Model Tenancy" in m.act or "Rent Control" in m.act for m in result.matches)
