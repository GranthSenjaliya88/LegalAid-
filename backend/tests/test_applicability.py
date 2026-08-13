"""
Test suite for State, City, Jurisdiction & Date Applicability Engine.
"""

from app.legal.applicability import evaluate_provision_applicability
from app.schemas.legal import RetrievalMatch


def test_applicability_jurisdiction_scoping():
    """Test state jurisdiction boundary enforcement."""
    match_delhi = RetrievalMatch(act="Delhi Rent Control Act, 1958", section="14", relevant_text="Tenant eviction", confidence=0.8, state="Delhi")
    match_all = RetrievalMatch(act="Model Tenancy Act, 2021", section="10", relevant_text="Security deposit", confidence=0.85, state="All")

    facts_gujarat = {"domain": "tenant", "state": "Gujarat", "incident": "deposit refund"}

    eval_delhi = evaluate_provision_applicability(match_delhi, facts_gujarat)
    eval_all = evaluate_provision_applicability(match_all, facts_gujarat)

    assert eval_delhi.applicability_status == "NOT_APPLICABLE"
    assert eval_all.applicability_status in {"APPLICABLE", "CONDITIONALLY_APPLICABLE"}
