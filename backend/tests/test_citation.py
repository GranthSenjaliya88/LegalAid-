"""
Test suite for Source-to-Claim Traceability and Citation Verification.
"""

from app.legal.claim_citation import verify_claims_against_retrieved_corpus
from app.schemas.legal import RetrievalMatch


def test_claim_citation_blocking():
    """Verify unsupported claims get blocked while supported claims pass."""
    matches = [
        RetrievalMatch(act="Model Tenancy Act, 2021", section="10", relevant_text="Security deposit refund within one month of vacating premises", confidence=0.9, state="All")
    ]

    claims = [
        "Landlord must refund security deposit within one month of vacating premises.",
        "Landlord can be imprisoned for 20 years under Section 999 Galactic Code."
    ]

    res = verify_claims_against_retrieved_corpus(claims, matches)
    assert res.total_claims == 2
    assert res.verified_claims_count == 1
    assert res.blocked_claims_count == 1
    assert res.claims[1].verification_status == "BLOCKED"
