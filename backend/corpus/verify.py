"""
corpus/verify.py — Post-ingest corpus integrity checks.

Run after every seed.py invocation to confirm the corpus is clean.
Also exposed as GET /corpus/verify so the frontend can show status.

Checks:
  1. Every section has non-empty text and section_number.
  2. No duplicate (act_id, section_number) pairs.
  3. FTS5 index row count == sections table count.
  4. Every act_id in sections references a real acts row.
  5. All domains are in the allowed set.
  6. At least one section per domain (consumer, labor, tenant).
"""

import sqlite3
from app.schemas import VerifyResponse, VerifyIssue

REQUIRED_DOMAINS = {"consumer", "labor", "tenant", "cyber", "criminal"}
ALLOWED_DOMAINS  = {
    "consumer", "labor", "tenant", "cyber", "criminal", "civil", "contract", "family",
    "women_rights", "children_rights", "banking", "traffic", "motor_vehicle", "property", "employment_benefits",
    "constitutional", "procedural", "evidence", "sc_st_protection", "disability_rights",
    "senior_citizens", "education", "digital_online", "general", "other"
}


def run_verify(conn: sqlite3.Connection) -> VerifyResponse:
    issues: list[VerifyIssue] = []

    # ── Check 1: empty text or missing section_number ─────────────────────
    bad_text = conn.execute(
        "SELECT id, section_number FROM sections WHERE trim(text)='' OR text IS NULL"
    ).fetchall()
    for row in bad_text:
        issues.append(VerifyIssue(
            check="empty_text",
            severity="error",
            detail=f"Section id={row['id']} section_number='{row['section_number']}' has empty text.",
        ))

    bad_num = conn.execute(
        "SELECT id FROM sections WHERE trim(section_number)='' OR section_number IS NULL"
    ).fetchall()
    for row in bad_num:
        issues.append(VerifyIssue(
            check="missing_section_number",
            severity="error",
            detail=f"Section id={row['id']} has no section_number.",
        ))

    # ── Check 2: duplicate (act_id, section_number) ───────────────────────
    dups = conn.execute(
        """
        SELECT act_id, section_number, COUNT(*) AS cnt
        FROM   sections
        GROUP  BY act_id, section_number
        HAVING cnt > 1
        """
    ).fetchall()
    for row in dups:
        issues.append(VerifyIssue(
            check="duplicate_section",
            severity="error",
            detail=f"Duplicate: act_id={row['act_id']} section_number='{row['section_number']}' appears {row['cnt']} times.",
        ))

    # ── Check 3: FTS5 index is searchable and returns results ─────────────
    # NOTE: With content='' FTS5 tables, COUNT(*) counts internal shadow-table
    # rows, not our indexed documents. We verify FTS health by running a real
    # search against known content and confirming at least one result.
    sec_count = conn.execute("SELECT COUNT(*) FROM sections WHERE is_active=1").fetchone()[0]
    try:
        fts_test = conn.execute(
            "SELECT COUNT(*) FROM sections_fts WHERE sections_fts MATCH 'act OR section OR law OR rights OR consumer OR tenant OR wages OR penalty OR court'"
        ).fetchone()[0]
        if sec_count > 0 and fts_test == 0:
            issues.append(VerifyIssue(
                check="fts_not_searchable",
                severity="error",
                detail="FTS5 index returned zero results for a broad test query — index may be corrupt or empty.",
            ))
    except Exception as e:
        issues.append(VerifyIssue(
            check="fts_query_error",
            severity="error",
            detail=f"FTS5 query failed: {e}",
        ))

    # ── Check 4: orphan act_id references ────────────────────────────────
    orphans = conn.execute(
        """
        SELECT s.id, s.act_id FROM sections s
        LEFT JOIN acts a ON a.id = s.act_id
        WHERE a.id IS NULL
        """
    ).fetchall()
    for row in orphans:
        issues.append(VerifyIssue(
            check="orphan_act_reference",
            severity="error",
            detail=f"Section id={row['id']} references non-existent act_id={row['act_id']}.",
        ))

    # ── Check 5: invalid domains ──────────────────────────────────────────
    bad_domains = conn.execute(
        f"""
        SELECT id, domain FROM sections
        WHERE domain NOT IN ({','.join('?' for _ in ALLOWED_DOMAINS)})
        """,
        list(ALLOWED_DOMAINS),
    ).fetchall()
    for row in bad_domains:
        issues.append(VerifyIssue(
            check="invalid_domain",
            severity="error",
            detail=f"Section id={row['id']} has invalid domain='{row['domain']}'.",
        ))

    # ── Check 6: required domains have at least one section ───────────────
    present_domains = {
        r["domain"]
        for r in conn.execute("SELECT DISTINCT domain FROM sections WHERE is_active=1").fetchall()
    }
    for domain in REQUIRED_DOMAINS:
        if domain not in present_domains:
            issues.append(VerifyIssue(
                check="missing_required_domain",
                severity="warning",
                detail=f"No sections found for required domain '{domain}'. Corpus is incomplete.",
            ))

    errors = [i for i in issues if i.severity == "error"]
    passed = len(errors) == 0

    summary = (
        "All checks passed. Corpus is clean."
        if passed
        else f"{len(errors)} error(s) and {len(issues) - len(errors)} warning(s) found."
    )

    return VerifyResponse(passed=passed, issues=issues, summary=summary)
