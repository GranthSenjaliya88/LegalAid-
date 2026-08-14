import json
from collections import Counter
from pathlib import Path

from app.legal.corpus_search import search_corpus
from app.services.classifier import classify_case_service


DATASET_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "evaluation"
    / "expanded_retrieval_eval.json"
)


def _load_cases() -> list[dict]:
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))


def test_expanded_dataset_has_broad_multilingual_coverage():
    cases = _load_cases()

    assert len(cases) >= 45
    assert len({case["id"] for case in cases}) == len(cases)
    assert {case["language"] for case in cases} == {"en", "hi", "hinglish"}
    assert len({case["expected_act"] for case in cases}) >= 15
    assert len({case["domain"] for case in cases}) >= 8

    language_counts = Counter(case["language"] for case in cases)
    assert min(language_counts.values()) >= 15


def test_expanded_dataset_classify_retrieve_recall_and_official_provenance():
    cases = _load_cases()
    hits = 0
    language_hits: Counter[str] = Counter()
    language_totals: Counter[str] = Counter()

    for case in cases:
        classification = classify_case_service(case["query"])
        assert classification.domain == case["domain"]

        response = search_corpus(
            domain=classification.domain,
            facts={"incident": case["query"]},
            limit=5,
        )
        language_totals[case["language"]] += 1

        expected = next(
            (
                match
                for match in response.matches[:5]
                if case["expected_act"].lower() in match.act.lower()
                and case["expected_section"].lower() == str(match.section).lower()
            ),
            None,
        )
        if expected is None:
            continue

        hits += 1
        language_hits[case["language"]] += 1
        assert "indiacode.nic.in" in (expected.official_source_url or "")
        assert expected.status == "CURRENT"

    assert hits / len(cases) >= 0.95
    for language, total in language_totals.items():
        assert language_hits[language] / total >= 0.90
