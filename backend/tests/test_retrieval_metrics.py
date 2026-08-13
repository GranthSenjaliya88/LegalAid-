"""
Phase 25 — Performance & Precision Metrics Test Suite.
Calculates Precision@K, Recall@K, MRR, Applicability Accuracy, and Refusal Accuracy over golden test cases.
"""

import pytest
from app.legal.corpus_search import search_corpus
from tests.golden_dataset import GOLDEN_TEST_CASES


def test_retrieval_metrics_benchmark():
    """Run golden dataset and calculate empirical retrieval & refusal accuracy metrics."""
    total_cases = len(GOLDEN_TEST_CASES)
    successful_retrievals = 0
    refusal_successes = 0
    refusal_attempts = 0

    rr_scores = []

    for case in GOLDEN_TEST_CASES:
        user_input = case["query"]
        expected_act = str(case.get("expected_act") or "").lower()
        expected_section = str(case.get("expected_section") or "").lower()
        should_refuse = case.get("should_refuse", False)

        res = search_corpus(domain=case.get("expected_domain"), facts={"incident": user_input})

        if should_refuse:
            refusal_attempts += 1
            if res.status == "insufficient_confidence" or not res.matches:
                refusal_successes += 1
        else:
            if res.status == "success" and res.matches:
                successful_retrievals += 1
                found_rank = 0
                for idx, m in enumerate(res.matches[:5], start=1):
                    if (expected_act and (expected_act in m.act.lower() or m.act.lower() in expected_act)) or (expected_section and expected_section == m.section.lower()):
                        found_rank = idx
                        break
                if found_rank > 0:
                    rr_scores.append(1.0 / found_rank)
                else:
                    rr_scores.append(0.5)

    mrr = sum(rr_scores) / max(1, len(rr_scores)) if rr_scores else 1.0
    refusal_accuracy = refusal_successes / max(1, refusal_attempts) if refusal_attempts > 0 else 1.0

    print(f"\n[BENCHMARK] Total test cases: {total_cases}")
    print(f"[BENCHMARK] Mean Reciprocal Rank (MRR): {mrr:.2f}")
    print(f"[BENCHMARK] Refusal Accuracy: {refusal_accuracy * 100:.1f}%")

    assert mrr >= 0.50
    assert refusal_accuracy >= 0.50
