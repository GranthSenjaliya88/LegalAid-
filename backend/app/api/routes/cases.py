"""
Case Intake and Lifecycle Management Routes (Phase 4 & Phase 17).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.repositories import CaseRepository
from app.core.security import sanitize_input
from app.schemas.case import CreateCaseRequest

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.post("", status_code=status.HTTP_201_CREATED, summary="Case Intake")
@router.post("/", status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_case(body: CreateCaseRequest, db: Session = Depends(get_db)):
    """
    Intake user legal problem description in Hindi or English.
    Validates input for size, empty content, and prompt injection.
    """
    clean_text = sanitize_input(body.text, language=body.language)

    case = CaseRepository.create_case(
        db=db,
        text=clean_text,
        language=body.language,
        session_id=body.session_id
    )

    return {
        "success": True,
        "data": {
            "case_id": case.id,
            "language": case.language,
            "status": case.status,
            "created_at": case.created_at.isoformat() + "Z"
        }
    }


@router.get("/{case_id}", summary="Get Case State")
def get_case_state(case_id: str, db: Session = Depends(get_db)):
    """Retrieve full case details and associated facts."""
    case = CaseRepository.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CASE_NOT_FOUND", "message": f"Case ID '{case_id}' not found."}
        )

    facts = case.facts
    facts_data = {
        "parties": facts.parties if facts else None,
        "incident": facts.incident if facts else None,
        "date": facts.date if facts else None,
        "location": facts.location if facts else None,
        "state": facts.state if facts else case.state,
        "subdomain": facts.subdomain if facts else case.subdomain,
        "amount": facts.amount if facts else None,
        "agreement_exists": facts.agreement_exists if facts else None,
        "notice_given": facts.notice_given if facts else None,
        "desired_outcome": facts.desired_outcome if facts else None,
        "urgency": facts.urgency if facts else case.urgency,
        "additional_facts": facts.additional_facts if facts else None,
    } if facts else None

    return {
        "success": True,
        "data": {
            "case_id": case.id,
            "session_id": case.session_id,
            "language": case.language,
            "original_text": case.original_text,
            "domain": case.domain,
            "subdomain": case.subdomain,
            "state": case.state,
            "urgency": case.urgency,
            "status": case.status,
            "created_at": case.created_at.isoformat() + "Z",
            "facts": facts_data
        }
    }


@router.delete("/{case_id}", summary="Privacy Cleanup - Delete Case")
def delete_case(case_id: str, db: Session = Depends(get_db)):
    """
    Purge associated case, case facts, retrieval results, and documents for privacy (Phase 17).
    """
    deleted = CaseRepository.delete_case(db, case_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CASE_NOT_FOUND", "message": f"Case ID '{case_id}' not found."}
        )

    return {
        "success": True,
        "data": {
            "message": f"Case '{case_id}' and all associated sensitive data purged successfully."
        }
    }
