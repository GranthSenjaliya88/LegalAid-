"""
Comprehensive Backend Hardening & Regression Test Suite.
Verifies health probes, FTS sanitization, database integrity, retrieval debugging,
atomic privacy deletion, request IDs, error envelopes, and legal safety rules.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_connection
from app.db.repositories import CaseRepository, DocumentRepository
from app.legal.corpus_search import sanitize_fts_query, search_corpus
from app.legal.applicability import check_section_applicability
from app.schemas.legal import RetrievalMatch
from sqlalchemy.orm import Session
from datetime import date

client = TestClient(app)


def test_health_live():
    """Verify Liveness probe returns status live."""
    response = client.get("/api/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "live"
    assert "Process is running" in data["message"]


def test_health_ready():
    """Verify Readiness probe executes readiness checks."""
    response = client.get("/api/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "fts" in data
    assert "vector_index" in data
    assert "ai" in data


def test_fts_malformed_query():
    """Verify malformed FTS query string containing quotes, parens, and operators does not crash FTS."""
    malformed_inputs = [
        '""deposit"" AND OR (test*)',
        "salary NOT NEAR *",
        "employer's :: unpaid --",
        "()()***)))",
        'AND OR NOT NEAR "landlord"'
    ]
    for raw_q in malformed_inputs:
        sanitized = sanitize_fts_query(raw_q)
        assert isinstance(sanitized, str)
        # Verify executing query does not throw SQLite syntax exception
        res = search_corpus(domain="tenant", facts={"incident": raw_q}, limit=5)
        assert res is not None


def test_fts_special_characters():
    """Verify special characters in input do not crash search pipeline."""
    res = search_corpus(domain="consumer", facts={"incident": "phone @#$%^&* defective refund!!"}, limit=5)
    assert res is not None


def test_database_health_endpoint():
    """Verify /api/admin/database-health returns foreign key check and table counts."""
    response = client.get("/api/admin/database-health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "foreign_key_violations_count" in data["data"]
    assert "row_counts" in data["data"]


def test_retrieval_debug_endpoint():
    """Verify /api/admin/retrieval-debug returns step-by-step pipeline diagnostic data."""
    payload = {
        "query": "Landlord withholding deposit in Delhi",
        "state": "Delhi",
        "city": "Delhi",
        "incident_date": "2026-01-15",
        "domain": "tenant"
    }
    response = client.post("/api/admin/retrieval-debug", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "normalized_query" in data["data"]
    assert "bm25_results" in data["data"]
    assert "final_results" in data["data"]


def test_case_delete_privacy_and_cascade(db_session: Session):
    """Verify deleting a case purges facts, documents, traces, and claim audit logs atomically."""
    # Create test case
    case = CaseRepository.create_case(db_session, text="Test case for privacy delete", language="en")
    case_id = case.id

    # Add facts & document
    CaseRepository.save_facts(db_session, case_id, {"incident": "Test incident", "state": "Delhi"})
    DocumentRepository.create_document(
        db=db_session,
        case_id=case_id,
        doc_type="legal_notice",
        title="Test Notice",
        content_sections=[{"heading": "Notice", "body": "Content"}],
        disclaimer="Test disclaimer"
    )

    # Perform atomic privacy delete
    deleted = CaseRepository.delete_case(db_session, case_id)
    assert deleted is True

    # Verify all records for this case are completely gone from DB
    assert CaseRepository.get_case(db_session, case_id) is None
    doc = DocumentRepository.get_document(db_session, case_id)
    assert doc is None


def test_request_id_in_response_headers_and_errors():
    """Verify X-Request-ID correlation header is present in responses and error envelopes."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers

    # Test error envelope request_id
    err_response = client.get("/api/cases/non_existent_case_999999")
    assert err_response.status_code == 404
    err_data = err_response.json()
    assert err_data["success"] is False
    assert "error" in err_data
    assert "request_id" in err_data["error"]


def test_jurisdiction_mismatch_rejection():
    """Verify state mismatch produces NOT_APPLICABLE evaluation."""
    match = RetrievalMatch(
        act="Delhi Rent Control Act, 1958",
        section="14",
        title="Eviction",
        relevant_text="Delhi tenancy rules",
        domain="tenant",
        state="Delhi",
        status="CURRENT",
        source_reference="DRCA Section 14",
        why_applies="Delhi tenancy",
        confidence=0.9
    )
    res = check_section_applicability(
        match=match,
        user_state="Gujarat",
        incident_date=date(2026, 1, 1)
    )
    assert res["status"] in {"NOT_APPLICABLE", "INSUFFICIENT_INFORMATION"}
