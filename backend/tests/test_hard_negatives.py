"""
Phase 24 — Hard Negative & Adversarial Evaluation Test Suite.
Tests system rejection / refusal against:
1. State jurisdiction mismatches (e.g. applying Delhi Rent Control in Gujarat).
2. Historical date invalidity (e.g. applying 2024 BNS to a 2022 crime).
3. Fake Acts and fake section numbers.
4. Prompt injection attempts.
"""

import pytest
from app.legal.applicability import evaluate_provision_applicability
from app.legal.corpus_search import search_corpus
from app.schemas.legal import RetrievalMatch


def test_hard_negative_state_mismatch():
    """Verify state mismatch triggers NOT_APPLICABLE or state warning."""
    match = RetrievalMatch(
        act="Delhi Rent Control Act, 1958",
        section="14",
        title="Protection of tenant against eviction",
        relevant_text="No order or decree for recovery of possession of any premises in Delhi...",
        plain_language_summary="Eviction protection in Delhi.",
        confidence=0.8,
        source_reference="Delhi Rent Control Act Section 14",
        state="Delhi",
        domain="tenant",
        status="CURRENT"
    )

    facts = {
        "incident": "My landlord in Gujarat hasn't returned deposit and wants to evict me.",
        "state": "Gujarat",
        "domain": "tenant"
    }

    eval_res = evaluate_provision_applicability(match, facts)
    assert eval_res.applicability_status == "NOT_APPLICABLE"
    assert any("Gujarat" in f or "Delhi" in f for f in eval_res.disqualifying_factors)


def test_hard_negative_date_mismatch():
    """Verify crime committed before July 1, 2024 disqualifies BNS in favor of historical IPC."""
    match = RetrievalMatch(
        act="Bharatiya Nyaya Sanhita, 2023 (BNS)",
        section="318",
        title="Cheating",
        relevant_text="Whoever cheats shall be punished...",
        plain_language_summary="Cheating penalty under 2023 code.",
        confidence=0.85,
        source_reference="BNS Section 318",
        state="All",
        domain="criminal",
        status="CURRENT"
    )

    facts = {
        "incident": "I was cheated in January 2022 by a fake builder.",
        "date": "2022-01-15",
        "domain": "criminal"
    }

    eval_res = evaluate_provision_applicability(match, facts)
    assert eval_res.applicability_status == "NOT_APPLICABLE"
    assert any("2022" in f or "July 1, 2024" in f for f in eval_res.disqualifying_factors)


def test_hard_negative_fake_act_search():
    """Verify non-existent/fake Act query returns insufficient confidence or zero verified matches."""
    res = search_corpus(
        domain="general",
        facts={"incident": "Galactic Space Interplanetary Code Section 99999"}
    )
    assert res.status == "insufficient_confidence" or len(res.matches) == 0

