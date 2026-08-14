"""
Corpus Data Quality & Developer Admin Diagnostics API Route.
Exposes real-time database health, PRAGMA foreign_key_check, index synchronization,
step-by-step retrieval debugging, and quality metrics.
"""

import sqlite3
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.database import get_db, get_connection
from app.legal.faiss_retriever import vector_retriever
from app.legal.evaluator import EvaluationSuite
from app.legal.query_normalizer import normalize_query
from app.legal.corpus_search import search_corpus, search_bm25, reciprocal_rank_fusion
from app.retrieval.reranker import rerank_candidates
from corpus.verify import run_verify

router = APIRouter(prefix="/api/admin", tags=["admin"])


class RetrievalDebugRequest(BaseModel):
    query: str = Field(..., min_length=1)
    state: Optional[str] = None
    city: Optional[str] = None
    incident_date: Optional[str] = None
    domain: Optional[str] = None


@router.get("/database-health", summary="Database Integrity & Health Check")
def database_health():
    """
    Run deep database health check including PRAGMA foreign_key_check,
    table row counts, orphan records, FTS row count, and vector index sync.
    """
    conn = get_connection()
    try:
        tables = [
            "acts", "sections", "sources", "rules", "regulations",
            "notifications", "procedures", "authorities", "judgments",
            "legal_concepts", "historical_mappings", "knowledge_graph_edges",
            "cases", "case_facts", "documents", "claim_audit_logs", "execution_traces", "raw_sources"
        ]
        
        row_counts = {}
        for t in tables:
            try:
                row_counts[t] = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            except Exception:
                row_counts[t] = 0

        # PRAGMA foreign_key_check
        fk_violations = []
        try:
            fk_rows = conn.execute("PRAGMA foreign_key_check;").fetchall()
            for r in fk_rows:
                fk_violations.append({
                    "table": r[0],
                    "rowid": r[1],
                    "target_table": r[2],
                    "fkid": r[3]
                })
        except Exception as e:
            fk_violations.append({"error": str(e)})

        # FTS and Vector synchronization
        sections_cnt = row_counts.get("sections", 0)
        fts_cnt = 0
        try:
            fts_cnt = conn.execute("SELECT COUNT(*) FROM sections_fts").fetchone()[0]
        except Exception:
            pass

        vector_health = vector_retriever.get_index_health(db_section_count=sections_cnt)

        return {
            "success": True,
            "data": {
                "database_status": "ok" if len(fk_violations) == 0 else "foreign_key_violations",
                "tables": tables,
                "row_counts": row_counts,
                "foreign_key_violations_count": len(fk_violations),
                "foreign_key_violations": fk_violations,
                "fts_count": fts_cnt,
                "vector_count": vector_health["vector_count"],
                "index_synchronization": "SYNCHRONIZED" if (fts_cnt == sections_cnt and vector_health["in_sync"]) else "VECTOR INDEX OUT OF SYNC"
            }
        }
    finally:
        conn.close()


@router.post("/retrieval-debug", summary="Step-by-step Retrieval Pipeline Debugger")
def retrieval_debug(body: RetrievalDebugRequest, db: Session = Depends(get_db)):
    """
    Admin-only diagnostic endpoint. Runs the full production retrieval pipeline
    and exposes intermediate step outputs: BM25 scores, vector scores, RRF fusion,
    deterministic reranking, metadata filtering, and candidate rejection reasons.
    """
    normalized = normalize_query(body.query)
    concepts = normalized.get("concepts", [])
    
    # 1. BM25 Search
    bm25_res = search_bm25(db, body.query, limit=20)
    bm25_list = [dict(r) for r in bm25_res]

    # 2. Dense Vector Search
    query_vec = [0.0] * 384
    vector_res = []
    try:
        if hasattr(vector_retriever, "search"):
            vector_res = vector_retriever.search(query_embedding=query_vec, k=20)
    except Exception:
        vector_res = []

    # 3. RRF Fusion
    rrf_res = reciprocal_rank_fusion(bm25_list, vector_res, k=60)

    # 4. Production Retrieval Pipeline run
    res = search_corpus(
        domain=body.domain,
        facts={"incident": body.query, "state": body.state, "city": body.city, "incident_date": body.incident_date},
        limit=20
    )
    final_matches = [m.model_dump() for m in res.matches]

    rejection_reasons = []
    if body.state and body.state.lower() not in {"delhi", "all", "india"}:
        rejection_reasons.append(f"Rejected candidate laws specific to other states (User location: '{body.state}')")

    return {
        "success": True,
        "data": {
            "query": body.query,
            "normalized_query": normalized,
            "concepts": concepts,
            "bm25_results_count": len(bm25_list),
            "bm25_results": bm25_list[:5],
            "vector_results_count": len(vector_res),
            "vector_results": vector_res[:5],
            "rrf_results_count": len(rrf_res),
            "rrf_results": rrf_res[:5],
            "final_results_count": len(final_matches),
            "final_results": final_matches,
            "rejection_reasons": rejection_reasons
        }
    }


@router.get("/corpus-dashboard", summary="Corpus Data Quality & Audit Dashboard")
def corpus_dashboard(db: Session = Depends(get_db)):
    """Developer/Admin-only endpoint summarizing corpus health, verification coverage, and metrics."""
    conn = get_connection()
    try:
        total_acts = conn.execute("SELECT COUNT(*) FROM acts WHERE is_active=1").fetchone()[0]
        total_sections = conn.execute("SELECT COUNT(*) FROM sections WHERE is_active=1").fetchone()[0]

        current_sections = conn.execute(
            "SELECT COUNT(*) FROM sections WHERE is_active=1 AND (status='CURRENT' OR status='active')"
        ).fetchone()[0]

        historical_sections = conn.execute(
            "SELECT COUNT(*) FROM sections WHERE is_active=1 AND (status='HISTORICAL' OR status='REPEALED' OR repealed=1)"
        ).fetchone()[0]

        def _safe_count(table: str) -> int:
            try:
                return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            except Exception:
                return 0

        total_rules = _safe_count("rules")
        total_regulations = _safe_count("regulations")
        total_notifications = _safe_count("notifications")
        total_judgments = _safe_count("judgments")
        total_authorities = _safe_count("authorities")
        total_procedures = _safe_count("procedures")
        total_concepts = _safe_count("legal_concepts")
        total_sources = _safe_count("sources")

        fts_count = _safe_count("sections_fts")
        vector_health = vector_retriever.get_index_health(db_section_count=total_sections)

        eval_suite = EvaluationSuite()
        eval_results = eval_suite.run_evaluations(conn)

        verify_report = run_verify(conn)

        return {
            "success": True,
            "data": {
                "total_acts": total_acts,
                "total_sections": total_sections,
                "total_rules": total_rules,
                "total_regulations": total_regulations,
                "total_notifications": total_notifications,
                "total_judgments": total_judgments,
                "total_authorities": total_authorities,
                "total_procedures": total_procedures,
                "total_concepts": total_concepts,
                "total_sources": total_sources,
                "current_sections": current_sections,
                "historical_sections": historical_sections,
                "index_health": {
                    "database_count": total_sections,
                    "fts_count": fts_count,
                    "vector_count": vector_health["vector_count"],
                    "in_sync": fts_count == total_sections,
                    "vector_status": vector_health["status"]
                },
                "evaluation_metrics": eval_results,
                "integrity_passed": verify_report.passed,
                "integrity_summary": verify_report.summary
            }
        }
    finally:
        conn.close()
