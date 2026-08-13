"""
Statute Corpus Search and Exploration Routes.
"""

import json
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db, get_connection
from app.db.models import LegalAct, LegalSection
from app.db.repositories import LegalRepository
from app.legal.corpus_search import search_corpus
from corpus.verify import run_verify

router = APIRouter(prefix="/api/corpus", tags=["corpus"])


@router.get("/stats", summary="Get Corpus Statistics")
def get_corpus_stats(db: Session = Depends(get_db)):
    """Retrieve corpus statistics by domain and counts."""
    acts_count = db.query(LegalAct).count()
    sections_count = db.query(LegalSection).count()

    domains = ["consumer", "labor", "tenant", "cyber", "criminal", "general"]
    domain_counts = {}
    for d in domains:
        domain_counts[d] = db.query(LegalSection).filter(LegalSection.domain == d).count()

    return {
        "success": True,
        "data": {
            "total_acts": acts_count,
            "total_sections": sections_count,
            "domains": domain_counts
        }
    }


@router.get("/acts", summary="List Statute Acts")
def list_acts(db: Session = Depends(get_db)):
    """Retrieve all indexed Legal Acts."""
    acts = LegalRepository.get_acts(db)
    result = []
    for a in acts:
        result.append({
            "id": a.id,
            "name": getattr(a, "short_name", "") or getattr(a, "long_name", ""),
            "short_name": getattr(a, "short_name", ""),
            "long_name": getattr(a, "long_name", ""),
            "year": getattr(a, "year", None),
            "jurisdiction": getattr(a, "jurisdiction", "INDIA"),
            "domain": getattr(a, "domain", "general"),
            "description": getattr(a, "long_name", ""),
            "source_url": getattr(a, "official_source_url", None),
            "section_count": len(a.sections) if getattr(a, "sections", None) else 0
        })
    return {"success": True, "data": result}


@router.get("/sections", summary="List Statute Sections")
def list_sections(
    act_id: Optional[int] = Query(None),
    domain: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Retrieve indexed sections filtered by act_id or domain."""
    sections = LegalRepository.get_sections(db, act_id=act_id, domain=domain, limit=limit)
    result = []
    for s in sections:
        result.append({
            "id": s.id,
            "act_id": s.act_id,
            "act_short_name": s.act.short_name if s.act else "",
            "section_number": s.section_number,
            "title": s.title,
            "text": s.text,
            "domain": s.domain,
            "language": s.language
        })
    return {"success": True, "data": result}


from app.legal.query_normalizer import normalize_query


@router.get("/search", summary="Search Statute Corpus")
def search_corpus_endpoint(
    q: str = Query(..., min_length=1),
    state: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Full-text and hybrid search on legal corpus with controlled query normalization."""
    normalized = normalize_query(q)
    res = search_corpus(domain=domain, facts={"incident": q, "state": state, "city": city}, limit=limit)
    matches_dict = [m.model_dump() for m in res.matches]
    return {
        "success": True,
        "query": q,
        "normalized": normalized,
        "count": len(matches_dict),
        "results": matches_dict,
        "data": {
            "query": q,
            "domain": domain,
            "status": res.status,
            "total": len(matches_dict),
            "results": matches_dict
        }
    }



@router.get("/authorities", summary="List Official Authorities")
def list_authorities(domain: Optional[str] = Query(None)):
    """Retrieve verified official government authorities directory."""
    conn = get_connection()
    try:
        sql = "SELECT * FROM authorities"
        params = []
        if domain:
            sql += " WHERE domain = ?"
            params.append(domain)
        rows = conn.execute(sql, params).fetchall()
        return {"success": True, "data": [dict(r) for r in rows]}
    finally:
        conn.close()


@router.get("/procedures", summary="List Official Procedures")
def list_procedures(domain: Optional[str] = Query(None)):
    """Retrieve step-by-step verified grievance resolution procedures."""
    conn = get_connection()
    try:
        sql = "SELECT * FROM procedures"
        params = []
        if domain:
            sql += " WHERE domain = ?"
            params.append(domain)
        rows = conn.execute(sql, params).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["procedure_steps"] = json.loads(d.get("procedure_steps_json") or "[]")
            d["required_documents"] = json.loads(d.get("required_documents_json") or "[]")
            results.append(d)
        return {"success": True, "data": results}
    finally:
        conn.close()


@router.get("/concepts", summary="List Legal Concept Synonyms")
def list_concepts(domain: Optional[str] = Query(None)):
    """Retrieve legal concept dictionary for English, Hindi, and Hinglish query expansion."""
    conn = get_connection()
    try:
        sql = "SELECT * FROM legal_concepts"
        params = []
        if domain:
            sql += " WHERE domain = ?"
            params.append(domain)
        rows = conn.execute(sql, params).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["english_synonyms"] = json.loads(d.get("english_synonyms_json") or "[]")
            d["hindi_synonyms"] = json.loads(d.get("hindi_synonyms_json") or "[]")
            d["hinglish_synonyms"] = json.loads(d.get("hinglish_synonyms_json") or "[]")
            results.append(d)
        return {"success": True, "data": results}
    finally:
        conn.close()


@router.get("/graph", summary="Get Legal Knowledge Graph Connections")
def get_graph_edges(source_id: Optional[str] = Query(None)):
    """Retrieve Knowledge Graph relationships across legal provisions."""
    conn = get_connection()
    try:
        sql = "SELECT * FROM knowledge_graph_edges"
        params = []
        if source_id:
            sql += " WHERE source_id LIKE ? OR target_id LIKE ?"
            params.extend([f"%{source_id}%", f"%{source_id}%"])
        rows = conn.execute(sql, params).fetchall()
        return {"success": True, "data": [dict(r) for r in rows]}
    finally:
        conn.close()


@router.get("/rules", summary="List Statutory Rules")
def list_rules(domain: Optional[str] = Query(None)):
    """Retrieve verified statutory rules."""
    conn = get_connection()
    try:
        sql = "SELECT * FROM rules"
        params = []
        if domain:
            sql += " WHERE domain = ?"
            params.append(domain)
        rows = conn.execute(sql, params).fetchall()
        return {"success": True, "data": [dict(r) for r in rows]}
    finally:
        conn.close()


@router.get("/regulations", summary="List Regulations")
def list_regulations(domain: Optional[str] = Query(None)):
    """Retrieve verified regulatory requirements."""
    conn = get_connection()
    try:
        sql = "SELECT * FROM regulations"
        params = []
        if domain:
            sql += " WHERE domain = ?"
            params.append(domain)
        rows = conn.execute(sql, params).fetchall()
        return {"success": True, "data": [dict(r) for r in rows]}
    finally:
        conn.close()


@router.get("/notifications", summary="List Official Notifications & Circulars")
def list_notifications(domain: Optional[str] = Query(None)):
    """Retrieve official government notifications and circulars."""
    conn = get_connection()
    try:
        sql = "SELECT * FROM notifications"
        params = []
        if domain:
            sql += " WHERE domain = ?"
            params.append(domain)
        rows = conn.execute(sql, params).fetchall()
        return {"success": True, "data": [dict(r) for r in rows]}
    finally:
        conn.close()


@router.get("/judgments", summary="List Landmark Judgments")
def list_judgments(domain: Optional[str] = Query(None)):
    """Retrieve verified Supreme Court and High Court precedent judgments."""
    conn = get_connection()
    try:
        sql = "SELECT * FROM judgments"
        params = []
        if domain:
            sql += " WHERE domain = ?"
            params.append(domain)
        rows = conn.execute(sql, params).fetchall()
        return {"success": True, "data": [dict(r) for r in rows]}
    finally:
        conn.close()


@router.get("/verify", summary="Run Corpus Integrity Check")
def verify_corpus():
    """Verify database corpus integrity against errors and missing fields."""
    conn = get_connection()
    try:
        report = run_verify(conn)
        return {
            "success": True,
            "data": {
                "passed": report.passed,
                "summary": report.summary,
                "issues": [{"check": i.check, "severity": i.severity, "detail": i.detail} for i in report.issues]
            }
        }
    finally:
        conn.close()

