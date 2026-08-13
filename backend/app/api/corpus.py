"""
Corpus router — /corpus/* endpoints.

All reads from the statute database flow through here.
Writes are intentionally absent: only seed.py / loader.py may
insert statute sections. The LLM is never given a write path.
"""

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
import sqlite3

from app.database import get_connection
from app.schemas import (
    ActOut, SectionOut, SearchResponse, SearchResult,
    VerifyResponse
)
from corpus.verify import run_verify

router = APIRouter(prefix="/corpus", tags=["corpus"])


# ─────────────────────────────────────────── Dependency ────────────────────

def db() -> sqlite3.Connection:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


# ─────────────────────────────────────────── Acts ──────────────────────────

@router.get("/acts", response_model=list[ActOut], summary="List all Acts in the corpus")
def list_acts(
    domain: Optional[str] = Query(None, description="Filter by domain: consumer|labor|tenant|criminal|general"),
    conn: sqlite3.Connection = Depends(db),
):
    if domain:
        rows = conn.execute(
            """
            SELECT a.*, COUNT(s.id) AS section_count
            FROM   acts a
            LEFT   JOIN sections s ON s.act_id = a.id AND s.is_active = 1
            WHERE  a.is_active = 1 AND a.domain = ?
            GROUP  BY a.id
            ORDER  BY a.year
            """,
            (domain,),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT a.*, COUNT(s.id) AS section_count
            FROM   acts a
            LEFT   JOIN sections s ON s.act_id = a.id AND s.is_active = 1
            WHERE  a.is_active = 1
            GROUP  BY a.id
            ORDER  BY a.year
            """,
        ).fetchall()
    return [_act_row_to_schema(r) for r in rows]


@router.get("/acts/{act_id}", response_model=ActOut, summary="Get a single Act")
def get_act(act_id: int, conn: sqlite3.Connection = Depends(db)):
    row = conn.execute(
        """
        SELECT a.*, COUNT(s.id) AS section_count
        FROM   acts a
        LEFT   JOIN sections s ON s.act_id = a.id AND s.is_active = 1
        WHERE  a.id = ? AND a.is_active = 1
        GROUP  BY a.id
        """,
        (act_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Act not found")
    return _act_row_to_schema(row)


# ─────────────────────────────────────────── Sections ──────────────────────

@router.get("/sections", response_model=list[SectionOut], summary="List sections (paginated)")
def list_sections(
    act_id: Optional[int] = Query(None),
    domain: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    conn: sqlite3.Connection = Depends(db),
):
    conditions = ["s.is_active = 1"]
    params: list = []
    if act_id:
        conditions.append("s.act_id = ?")
        params.append(act_id)
    if domain:
        conditions.append("s.domain = ?")
        params.append(domain)
    where = " AND ".join(conditions)
    rows = conn.execute(
        f"""
        SELECT s.*, a.short_name AS act_short_name
        FROM   sections s
        JOIN   acts a ON a.id = s.act_id
        WHERE  {where}
        ORDER  BY s.act_id, s.id
        LIMIT  ? OFFSET ?
        """,
        params + [limit, skip],
    ).fetchall()
    return [_section_row_to_schema(r) for r in rows]


@router.get("/sections/{section_id}", response_model=SectionOut, summary="Get a single section by ID")
def get_section(section_id: int, conn: sqlite3.Connection = Depends(db)):
    row = conn.execute(
        """
        SELECT s.*, a.short_name AS act_short_name
        FROM   sections s
        JOIN   acts a ON a.id = s.act_id
        WHERE  s.id = ? AND s.is_active = 1
        """,
        (section_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Section not found")
    return _section_row_to_schema(row)


# ─────────────────────────────────────────── Search ────────────────────────

@router.get("/search", response_model=SearchResponse, summary="Full-text search across statute sections")
def search_sections(
    q: str = Query(..., min_length=2, description="Search query (English or Hindi)"),
    domain: Optional[str] = Query(None, description="Restrict to a legal domain"),
    limit: int = Query(10, ge=1, le=50),
    conn: sqlite3.Connection = Depends(db),
):
    """
    FTS5 BM25 search over statute sections.

    Returns sections ranked by relevance (bm25_score — lower = more relevant
    in SQLite FTS5). Each result includes the full section text so the caller
    can verify the citation is real.
    """
    # Sanitise query: FTS5 interprets special chars as operators
    safe_q = _sanitise_fts_query(q)

    if domain:
        rows = conn.execute(
            """
            SELECT s.id, s.act_id, s.section_number, s.title, s.text,
                   s.domain, s.keywords, a.short_name AS act_short_name,
                   bm25(sections_fts) AS score
            FROM   sections_fts
            JOIN   sections s ON s.id = sections_fts.rowid
            JOIN   acts     a ON a.id = s.act_id
            WHERE  sections_fts MATCH ? AND s.domain = ? AND s.is_active = 1
            ORDER  BY score
            LIMIT  ?
            """,
            (safe_q, domain, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT s.id, s.act_id, s.section_number, s.title, s.text,
                   s.domain, s.keywords, a.short_name AS act_short_name,
                   bm25(sections_fts) AS score
            FROM   sections_fts
            JOIN   sections s ON s.id = sections_fts.rowid
            JOIN   acts     a ON a.id = s.act_id
            WHERE  sections_fts MATCH ? AND s.is_active = 1
            ORDER  BY score
            LIMIT  ?
            """,
            (safe_q, limit),
        ).fetchall()

    results = [
        SearchResult(
            section_id=r["id"],
            act_id=r["act_id"],
            act_short_name=r["act_short_name"],
            section_number=r["section_number"],
            title=r["title"],
            text=r["text"],
            domain=r["domain"],
            keywords=json.loads(r["keywords"] or "[]"),
            bm25_score=r["score"],
        )
        for r in rows
    ]
    return SearchResponse(query=q, domain_filter=domain, total=len(results), results=results)


# ─────────────────────────────────────────── Verify ────────────────────────

@router.get("/verify", response_model=VerifyResponse, summary="Run corpus integrity checks")
def verify_corpus(conn: sqlite3.Connection = Depends(db)):
    """
    Runs all integrity checks and returns a structured report.
    Call this after any seeding operation to confirm the corpus is clean.
    """
    return run_verify(conn)


# ─────────────────────────────────────────── Helpers ───────────────────────

def _sanitise_fts_query(q: str) -> str:
    """Wrap each token in double-quotes to prevent FTS5 operator injection."""
    tokens = q.strip().split()
    safe = " OR ".join(f'"{t}"' for t in tokens if t)
    return safe or '""'


def _act_row_to_schema(r: sqlite3.Row) -> ActOut:
    d = dict(r)
    return ActOut(**d)


def _section_row_to_schema(r: sqlite3.Row) -> SectionOut:
    d = dict(r)
    d["keywords"] = json.loads(d.get("keywords") or "[]")
    # Remove fields not in schema
    d.pop("embedding_json", None)
    return SectionOut(**d)
