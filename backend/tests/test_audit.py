"""
Test suite for 14-Point Legal Answer Audit Engine.
"""

from app.legal.answer_audit import audit_final_legal_answer
from app.legal.claim_citation import verify_claims_against_retrieved_corpus
from app.schemas.legal import RetrievalMatch


def test_answer_audit_pass():
    """Verify legal answer passes 14-point compliance audit."""
    matches = [
        RetrievalMatch(act="Model Tenancy Act, 2021", section="10", relevant_text="Security deposit refund within one month", confidence=0.9, state="All")
    ]
    claims_res = verify_claims_against_retrieved_corpus(
        ["Security deposit refund within one month."], matches
    )

    facts = {"domain": "tenant", "state": "Karnataka", "incident": "deposit refund"}

    audit_res = audit_final_legal_answer(
        user_query="My landlord has not returned my security deposit",
        extracted_facts=facts,
        retrieved_matches=matches,
        claims_verification=claims_res,
        raw_explanation={"rights": ["Right to security deposit refund"]}
    )

    assert audit_res is not None
    assert audit_res.total_checks == 14
    assert audit_res.audit_status in {"PASS", "WARNING"}
