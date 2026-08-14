"""
LegalAId — Retrieval Agent (Step 3)

INPUT : classified_domain and extracted_facts from Step 2.
OUTPUT: RetrievalOutput — list of matching statute sections retrieved from the database.

Rules:
- Uses SQLite FTS5 index and domain filter to locate matching statute sections.
- Strictly returns real statute rows from the SQLite database.
"""

from __future__ import annotations

import logging
import sqlite3
import re
from typing import Any

from app.database import get_connection
from app.schemas import ClassifierOutput, RetrievalOutput, RetrievedSection

logger = logging.getLogger(__name__)


def retrieve_sections(classifier_output: ClassifierOutput, limit: int = 5) -> RetrievalOutput:
    """ 
    Query the statute corpus using classified_domain and extracted_facts.
    Returns ranked list of matching statute sections from SQLite.
    """
    domain = classifier_output.classified_domain
    facts  = classifier_output.extracted_facts

    # Build search query terms from extracted facts
    query_parts = []
    if facts.issue_summary:
        clean_summary = re.sub(r"[^\w\s]", " ", facts.issue_summary)
        query_parts.append(clean_summary)
    if facts.user_goal:
        clean_goal = re.sub(r"[^\w\s]", " ", facts.user_goal)
        query_parts.append(clean_goal)
    if facts.amounts:
        query_parts.append("amount refund money deposit salary")

    combined_query = " ".join(query_parts).strip()
    if not combined_query:
        combined_query = domain

    # Extract keywords for FTS matching
    words = [w for w in re.findall(r"\w+", combined_query.lower()) if len(w) > 2]
    fts_query = " OR ".join(words[:8]) if words else domain

    conn = get_connection()
    try:
        sections = _search_db(conn, fts_query=fts_query, domain_filter=domain, limit=limit)
        
        # If domain filter returned 0 results or domain is 'other', search broadly
        if not sections and domain != "other":
            sections = _search_db(conn, fts_query=fts_query, domain_filter=None, limit=limit)

        if not sections:
            # Fallback to fetching all sections in domain
            sections = _get_default_domain_sections(conn, domain=domain, limit=limit)

        return RetrievalOutput(
            query_used=combined_query[:100],
            domain_filter=domain if domain != "other" else None,
            total_found=len(sections),
            sections=sections,
        )
    finally:
        conn.close()


def _search_db(
    conn: sqlite3.Connection,
    fts_query: str,
    domain_filter: str | None,
    limit: int = 5
) -> list[RetrievedSection]:
    """Execute FTS5 search joining with acts table."""
    params: list[Any] = [fts_query]
    domain_clause = ""
    if domain_filter and domain_filter in {"consumer", "labor", "tenant", "criminal"}:
        domain_clause = " AND s.domain = ? "
        params.append(domain_filter)

    params.append(limit)

    sql = f"""
        SELECT 
            s.id AS section_id,
            a.short_name AS act_short_name,
            a.name AS act_name,
            s.section_number,
            s.title,
            s.text,
            s.domain,
            fts.rank AS bm25_score
        FROM sections_fts fts
        JOIN sections s ON s.id = fts.rowid
        JOIN acts a ON a.id = s.act_id
        WHERE sections_fts MATCH ?
          AND s.is_active = 1
          {domain_clause}
        ORDER BY fts.rank ASC
        LIMIT ?
    """

    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError as exc:
        logger.warning("FTS query failed (%s) — using LIKE fallback.", exc)
        return _fallback_like_search(conn, fts_query, domain_filter, limit)

    results = []
    for r in rows:
        results.append(RetrievedSection(
            section_id=r["section_id"],
            act_short_name=r["act_short_name"],
            act_name=r["act_name"],
            section_number=r["section_number"],
            title=r["title"],
            text=r["text"],
            domain=r["domain"],
            score=round(float(r["bm25_score"]), 4),
        ))
    return results


def _fallback_like_search(
    conn: sqlite3.Connection,
    query_text: str,
    domain_filter: str | None,
    limit: int = 5
) -> list[RetrievedSection]:
    """Fallback search using SQLite LIKE when FTS syntax encounters syntax errors."""
    words = [w for w in re.findall(r"\w+", query_text.lower()) if len(w) > 3][:3]
    if not words:
        words = ["section"]

    like_clauses = " OR ".join(["s.text LIKE ? OR s.title LIKE ?" for _ in words])
    params = []
    for w in words:
        params.extend([f"%{w}%", f"%{w}%"])

    domain_clause = ""
    if domain_filter and domain_filter in {"consumer", "labor", "tenant", "criminal"}:
        domain_clause = " AND s.domain = ? "
        params.append(domain_filter)

    params.append(limit)

    sql = f"""
        SELECT 
            s.id AS section_id,
            a.short_name AS act_short_name,
            a.name AS act_name,
            s.section_number,
            s.title,
            s.text,
            s.domain
        FROM sections s
        JOIN acts a ON a.id = s.act_id
        WHERE s.is_active = 1 AND ({like_clauses}) {domain_clause}
        LIMIT ?
    """
    rows = conn.execute(sql, params).fetchall()
    return [
        RetrievedSection(
            section_id=r["section_id"],
            act_short_name=r["act_short_name"],
            act_name=r["act_name"],
            section_number=r["section_number"],
            title=r["title"],
            text=r["text"],
            domain=r["domain"],
            score=0.5,
        )
        for r in rows
    ]


def _get_default_domain_sections(
    conn: sqlite3.Connection,
    domain: str,
    limit: int = 5
) -> list[RetrievedSection]:
    """Get top sections for a domain if query yields no FTS hits."""
    params: list[Any] = []
    where_clause = " WHERE s.is_active = 1 "
    if domain in {"consumer", "labor", "tenant", "criminal"}:
        where_clause += " AND s.domain = ? "
        params.append(domain)
    params.append(limit)

    sql = f"""
        SELECT 
            s.id AS section_id,
            a.short_name AS act_short_name,
            a.name AS act_name,
            s.section_number,
            s.title,
            s.text,
            s.domain
        FROM sections s
        JOIN acts a ON a.id = s.act_id
        {where_clause}
        ORDER BY s.id ASC
        LIMIT ?
    """
    rows = conn.execute(sql, params).fetchall()
    return [
        RetrievedSection(
            section_id=r["section_id"],
            act_short_name=r["act_short_name"],
            act_name=r["act_name"],
            section_number=r["section_number"],
            title=r["title"],
            text=r["text"],
            domain=r["domain"],
            score=1.0,
        )
        for r in rows
    ]
