"""
Document Drafting, Editing, and PDF Export Routes (Phases 10, 11, 12).
"""

import json
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.repositories import CaseRepository, DocumentRepository
from app.services.retriever import retrieve_legal_sections
from app.services.document_drafter import draft_document_service
from app.services.pdf_generator import generate_pdf_bytes
from app.schemas.document import UpdateDocumentRequest, DocumentResponseData

router = APIRouter(tags=["documents"])


@router.post("/api/cases/{case_id}/document", summary="Phase 10 - Document Generation")
def generate_document_route(
    case_id: str,
    doc_type: str = Query("legal_notice", description="complaint|consumer_complaint|labor_complaint|tenant_notice|legal_notice"),
    db: Session = Depends(get_db)
):
    """
    Generate structured legal document template incorporating verified legal sections.
    """
    case = CaseRepository.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CASE_NOT_FOUND", "message": f"Case '{case_id}' not found."}
        )

    facts_dict = {
        "parties": case.facts.parties if case.facts else None,
        "incident": case.facts.incident if case.facts else case.original_text,
        "amount": case.facts.amount if case.facts else None,
        "desired_outcome": case.facts.desired_outcome if case.facts else None
    }

    retrieval_res = retrieve_legal_sections(domain=case.domain, facts=facts_dict)
    doc_res = draft_document_service(
        db=db,
        case_id=case_id,
        doc_type=doc_type,
        verified_matches=retrieval_res.matches,
        case_facts=facts_dict
    )

    return {
        "success": True,
        "data": doc_res.model_dump()
    }


@router.get("/api/documents/{document_id}", summary="Phase 11 - Get Document")
def get_document_route(document_id: str, db: Session = Depends(get_db)):
    """Retrieve document details and sections by document ID."""
    doc = DocumentRepository.get_document(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DOCUMENT_NOT_FOUND", "message": f"Document '{document_id}' not found."}
        )

    sections_val = json.loads(doc.content_json) if isinstance(doc.content_json, str) else doc.content_json
    warnings_val = json.loads(doc.quality_warnings_json) if isinstance(doc.quality_warnings_json, str) else (doc.quality_warnings_json or [])

    return {
        "success": True,
        "data": {
            "document_id": doc.id,
            "case_id": doc.case_id,
            "type": doc.type,
            "title": doc.title,
            "sections": sections_val,
            "quality_score": doc.quality_score,
            "quality_warnings": warnings_val,
            "disclaimer": doc.disclaimer,
            "created_at": doc.created_at.isoformat() + "Z"
        }
    }


@router.put("/api/documents/{document_id}", summary="Phase 11 - Edit Document")
def update_document_route(document_id: str, body: UpdateDocumentRequest, db: Session = Depends(get_db)):
    """Update editable document sections and title, and recalculate quality score."""
    sections_objs = [s for s in body.sections]
    sections_dicts = [s.model_dump() for s in body.sections]

    # Recalculate Quality Score
    from app.services.document_drafter import evaluate_document_quality
    quality_score, warnings = evaluate_document_quality(sections_objs, {})

    updated = DocumentRepository.update_document(
        db=db,
        doc_id=document_id,
        content_sections=sections_dicts,
        title=body.title,
        quality_score=quality_score,
        quality_warnings=warnings
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DOCUMENT_NOT_FOUND", "message": f"Document '{document_id}' not found."}
        )

    sections_val = json.loads(updated.content_json) if isinstance(updated.content_json, str) else updated.content_json
    warnings_val = json.loads(updated.quality_warnings_json) if isinstance(updated.quality_warnings_json, str) else (updated.quality_warnings_json or [])

    return {
        "success": True,
        "data": {
            "document_id": updated.id,
            "case_id": updated.case_id,
            "type": updated.type,
            "title": updated.title,
            "sections": sections_val,
            "quality_score": updated.quality_score,
            "quality_warnings": warnings_val,
            "disclaimer": updated.disclaimer,
            "updated_at": updated.created_at.isoformat() + "Z"
        }
    }


@router.get("/api/documents/{document_id}/pdf", summary="Phase 12 - PDF Export")
def export_pdf_route(document_id: str, db: Session = Depends(get_db)):
    """
    Generate and download binary PDF of legal document with mandatory disclaimer.
    """
    doc = DocumentRepository.get_document(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DOCUMENT_NOT_FOUND", "message": f"Document '{document_id}' not found."}
        )

    sections_val = json.loads(doc.content_json) if isinstance(doc.content_json, str) else doc.content_json

    doc_data = {
        "document_id": doc.id,
        "title": doc.title,
        "sections": sections_val,
        "disclaimer": doc.disclaimer
    }

    pdf_bytes = generate_pdf_bytes(doc_data)

    filename = f"LegalAId_{doc.type}_{doc.id[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
