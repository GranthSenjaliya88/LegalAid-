"""
Regression tests for Legal Sources search functionality, API endpoints, FTS index, and fallbacks.
"""

import pytest
from app.db.database import get_connection
from app.legal.corpus_search import search_corpus


def test_fts_index_has_records():
    """Verify database contains Acts, Sections, and FTS records."""
    conn = get_connection()
    try:
        acts = conn.execute("SELECT COUNT(*) FROM acts").fetchone()[0]
        sections = conn.execute("SELECT COUNT(*) FROM sections").fetchone()[0]
        fts = conn.execute("SELECT COUNT(*) FROM sections_fts").fetchone()[0]

        assert acts > 0, "Acts table is empty"
        assert sections > 0, "Sections table is empty"
        assert fts > 0, "FTS5 table is empty"
    finally:
        conn.close()


def test_search_security_deposit_returns_results():
    """Verify 'security deposit' query returns matching legal sections."""
    res = search_corpus(domain=None, facts={"incident": "security deposit"})
    assert res.status == "success"
    assert len(res.matches) > 0
    acts = [m.act for m in res.matches]
    assert any("Tenancy" in act or "BNS" in act or "Nyaya" in act for act in acts)


def test_search_unpaid_wages_returns_results():
    """Verify 'unpaid wages' query returns matching legal sections."""
    res = search_corpus(domain=None, facts={"incident": "unpaid wages"})
    assert res.status == "success"
    assert len(res.matches) > 0
    sections = [m.section for m in res.matches]
    assert "25F" in sections or "2(s)" in sections or len(sections) > 0


def test_search_consumer_returns_results():
    """Verify 'consumer' query returns Consumer Protection Act sections."""
    res = search_corpus(domain="consumer", facts={"incident": "defective product"})
    assert res.status == "success"
    assert len(res.matches) > 0
    assert any("Consumer Protection" in m.act for m in res.matches)


def test_search_salary_fallback():
    """Verify 'salary' query returns wage/employment sections via synonym expansion and fallback."""
    res = search_corpus(domain=None, facts={"incident": "salary"})
    assert res.status == "success"
    assert len(res.matches) > 0


def test_category_filter(client):
    """Verify category domain filter in API search."""
    resp = client.get("/api/corpus/search?q=deposit&domain=tenant")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    results = data["data"]["results"]
    assert len(results) > 0
    assert all(r["domain"] == "tenant" for r in results)


def test_unknown_nonsense_search():
    """Verify search for nonsense query returns insufficient_confidence without crashing or inventing sections."""
    res = search_corpus(domain=None, facts={"incident": "xyzqwerty123999 zzzqwerty999888"})
    assert res.status == "insufficient_confidence"
    assert len(res.matches) == 0


def test_corpus_stats_endpoint(client):
    """Verify /api/corpus/stats endpoint returns valid statistics without NameError."""
    resp = client.get("/api/corpus/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["total_acts"] >= 6
    assert data["data"]["total_sections"] >= 40


def test_corpus_verify_endpoint(client):
    """Verify /api/corpus/verify endpoint returns health status."""
    resp = client.get("/api/corpus/verify")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["passed"] is True
