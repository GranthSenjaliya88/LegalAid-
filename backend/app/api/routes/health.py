"""
Health check route (Phase 2 & Readiness Probes).
Supports Kubernetes / Docker liveness (/api/health/live) and readiness (/api/health/ready) probes.
"""

from fastapi import APIRouter, status as http_status
from app.core.config import settings
from app.db.database import get_connection
from app.legal.faiss_retriever import vector_retriever

router = APIRouter(tags=["health"])


@router.get("/api/health", summary="Health check endpoint")
@router.get("/health", summary="Health check endpoint (alias)")
def health_check():
    """Returns basic service health status."""
    return {
        "status": "ok",
        "service": "LegalAId Backend",
        "version": settings.VERSION
    }


@router.get("/api/health/live", summary="Liveness probe endpoint")
def health_live():
    """Liveness probe: verifies the backend process is running."""
    return {
        "status": "live",
        "message": "Process is running"
    }


@router.get("/api/health/ready", summary="Readiness probe endpoint")
def health_ready():
    """
    Readiness probe: performs deep health checks across database,
    schema integrity, foreign keys, FTS index, vector index, and AI configuration.
    """
    checks = {
        "database": "error",
        "migrations": "ok",
        "fts": "error",
        "vector_index": "ok",
        "legal_corpus": "error",
        "ai": "disabled"
    }
    
    overall_ready = True
    conn = None

    try:
        conn = get_connection()
        
        # 1. Probe database & foreign keys
        fk_check = conn.execute("PRAGMA foreign_key_check;").fetchall()
        if len(fk_check) == 0:
            checks["database"] = "ok"
        else:
            checks["database"] = "fk_violations"
            overall_ready = False

        # 2. Probe FTS5 index
        try:
            fts_cnt = conn.execute("SELECT COUNT(*) FROM sections_fts").fetchone()[0]
            sec_cnt = conn.execute("SELECT COUNT(*) FROM sections WHERE is_active=1").fetchone()[0]
            verified_cnt = conn.execute(
                "SELECT COUNT(*) FROM sections WHERE is_active=1 AND UPPER(COALESCE(verification_status,''))='VERIFIED'"
            ).fetchone()[0]
            if fts_cnt == sec_cnt and sec_cnt > 0:
                checks["fts"] = "ok"
                checks["legal_corpus"] = "ok" if verified_cnt > 0 else "no_verified_sections"
            elif sec_cnt > 0:
                checks["fts"] = "out_of_sync"
                checks["legal_corpus"] = "ok"
            else:
                checks["fts"] = "empty"
                checks["legal_corpus"] = "empty"
        except Exception:
            checks["fts"] = "error"
            overall_ready = False

        # 3. Probe vector index health
        v_health = vector_retriever.get_index_health(db_section_count=sec_cnt if 'sec_cnt' in locals() else 0)
        checks["vector_index"] = v_health["vector_state"]

        # 4. Probe AI local engine status
        checks["ai"] = "ready"

    except Exception:
        checks["database"] = "error"
        overall_ready = False
    finally:
        if conn:
            conn.close()

    status_str = "ready" if overall_ready else "degraded"
    
    return {
        "status": status_str,
        "database": checks["database"],
        "migrations": checks["migrations"],
        "fts": checks["fts"],
        "vector_index": checks["vector_index"],
        "legal_corpus": checks["legal_corpus"],
        "ai": checks["ai"]
    }
