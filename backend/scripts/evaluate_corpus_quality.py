"""Measure corpus quality and retrieval accuracy without modifying the database."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.database import get_connection, init_db  # noqa: E402
from app.legal.corpus_search import search_corpus  # noqa: E402
from tests.golden_dataset import GOLDEN_TEST_CASES  # noqa: E402


def _scalar(conn, sql: str) -> int:
    return int(conn.execute(sql).fetchone()[0])


def corpus_metrics(conn) -> dict:
    total = _scalar(conn, "SELECT COUNT(*) FROM sections WHERE is_active=1")
    verified = _scalar(
        conn,
        "SELECT COUNT(*) FROM sections WHERE is_active=1 AND UPPER(COALESCE(verification_status,''))='VERIFIED'",
    )
    official = _scalar(
        conn,
        "SELECT COUNT(*) FROM sections WHERE is_active=1 AND COALESCE(official_source_url, source_url, '') <> ''",
    )
    hashed = _scalar(
        conn,
        "SELECT COUNT(*) FROM sections WHERE is_active=1 AND COALESCE(content_hash, '') <> ''",
    )
    duplicates = _scalar(
        conn,
        """
        SELECT COUNT(*) FROM (
          SELECT act_id, section_number FROM sections WHERE is_active=1
          GROUP BY act_id, section_number HAVING COUNT(*) > 1
        )
        """,
    )
    by_domain = {
        row["domain"] or "unknown": row["count"]
        for row in conn.execute(
            "SELECT domain, COUNT(*) AS count FROM sections WHERE is_active=1 GROUP BY domain ORDER BY count DESC"
        )
    }
    latest_ingestion_row = conn.execute(
        """
        SELECT status, acts_discovered, sections_discovered, sections_inserted,
               sections_updated, sections_unchanged, sections_rejected, completed_at
        FROM ingestion_runs ORDER BY id DESC LIMIT 1
        """
    ).fetchone()
    latest_ingestion = dict(latest_ingestion_row) if latest_ingestion_row else None
    return {
        "acts": _scalar(conn, "SELECT COUNT(*) FROM acts WHERE is_active=1"),
        "sections": total,
        "verified_sections": verified,
        "verified_coverage": round(verified / max(1, total), 4),
        "official_source_coverage": round(official / max(1, total), 4),
        "content_hash_coverage": round(hashed / max(1, total), 4),
        "duplicate_section_groups": duplicates,
        "section_versions": _scalar(conn, "SELECT COUNT(*) FROM section_versions"),
        "historical_rejected_records": _scalar(conn, "SELECT COUNT(*) FROM ingestion_rejections"),
        "latest_ingestion": latest_ingestion,
        "by_domain": by_domain,
    }


def retrieval_metrics(limit: int = 5) -> dict:
    reciprocal_ranks: list[float] = []
    top_k_hits = 0
    evaluated = 0
    refusals = 0
    correct_refusals = 0
    failures: list[dict] = []

    for case in GOLDEN_TEST_CASES:
        should_refuse = bool(case.get("should_refuse")) or case.get("expected_confidence") == "INSUFFICIENT INFORMATION"
        result = search_corpus(
            domain=case.get("expected_domain"),
            facts={"incident": case["query"], "state": case.get("expected_state")},
            limit=limit,
        )
        if should_refuse:
            refusals += 1
            if result.status == "insufficient_confidence" or not result.matches:
                correct_refusals += 1
            else:
                failures.append({"id": case["id"], "reason": "expected_refusal"})
            continue

        evaluated += 1
        expected_act = str(case.get("expected_act") or "").lower().strip()
        expected_section = str(case.get("expected_section") or "").lower().strip()
        rank = 0
        for index, match in enumerate(result.matches[:limit], start=1):
            act_text = f"{match.act} {match.source_reference or ''}".lower()
            section_text = str(match.section).lower()
            act_hit = not expected_act or expected_act in act_text or act_text in expected_act
            section_hit = not expected_section or expected_section == section_text
            if act_hit and section_hit:
                rank = index
                break
        if rank:
            top_k_hits += 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)
            failures.append({"id": case["id"], "reason": "expected_provision_not_in_top_k"})

    return {
        "evaluated_retrieval_cases": evaluated,
        "recall_at_k": round(top_k_hits / max(1, evaluated), 4),
        "mrr": round(sum(reciprocal_ranks) / max(1, len(reciprocal_ranks)), 4),
        "refusal_accuracy": round(correct_refusals / max(1, refusals), 4),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-retrieval", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    init_db()
    conn = get_connection()
    try:
        report = {"corpus": corpus_metrics(conn)}
    finally:
        conn.close()
    if not args.skip_retrieval:
        report["retrieval"] = retrieval_metrics()

    encoded = json.dumps(report, ensure_ascii=False, indent=2)
    print(encoded)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
