"""
Document Drafter Service (Phase 10 & 11).
Generates template-controlled legal documents incorporating verified legal sections.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.ai.client import ai_client
from app.schemas.document import DocumentResponseData, DocumentSection
from app.db.repositories import DocumentRepository
from app.schemas.legal import RetrievalMatch

MANDATORY_DISCLAIMER = (
    "DISCLAIMER: This document is generated for informational purposes "
    "and is not legal advice. Consult a licensed advocate for representation."
)

SUPPORTED_DOC_TYPES = {
    "complaint": "Legal Complaint",
    "consumer_complaint": "Consumer Dispute Complaint",
    "consumer_notice": "Consumer Dispute Legal Notice",
    "labor_complaint": "Labor Commissioner Complaint",
    "salary_demand": "Salary & Wage Demand Notice",
    "tenant_notice": "Tenant Security Deposit Notice",
    "rental_dispute_notice": "Rental Dispute Notice",
    "cyber_complaint": "Cyber Crime & Financial Fraud Complaint",
    "legal_notice": "Formal Legal Notice"
}


def evaluate_document_quality(sections: List[DocumentSection], case_facts: Dict[str, Any]) -> tuple[float, list[str]]:
    """
    Run Document Quality Checker (Requirement #25).
    Evaluates 10 structural elements and outputs score (out of 10) and warnings.
    """
    score = 10.0
    warnings: list[str] = []

    all_content = " ".join([f"{s.title} {s.content}" for s in sections]).lower()

    # Check 1: Sender / Parties
    if "from:" not in all_content and not case_facts.get("parties"):
        score -= 1.0
        warnings.append("Sender / Complainant details are incomplete.")

    # Check 2: Recipient
    if "to:" not in all_content and "counterparty" in all_content:
        score -= 1.0
        warnings.append("Recipient / Counterparty specific name and address are missing.")

    # Check 3: Date
    if "[current date]" in all_content or "date:" not in all_content:
        score -= 0.5
        warnings.append("Date field contains placeholder or is unspecific.")

    # Check 4: Subject
    if "subject" not in all_content:
        score -= 1.0
        warnings.append("Formal Subject line is missing.")

    # Check 5: Facts
    if "facts" not in all_content and len(all_content) < 200:
        score -= 1.5
        warnings.append("Statement of facts is brief or incomplete.")

    # Check 6: Legal Grounds
    if "section" not in all_content and "act" not in all_content:
        score -= 2.0
        warnings.append("Specific statutory sections and legal grounds are missing.")

    # Check 7: Demand / Notice Period
    if "demand" not in all_content and "15 days" not in all_content and "refund" not in all_content:
        score -= 1.0
        warnings.append("Clear demand or notice compliance period is missing.")

    # Check 8: Evidence reference
    if "evidence" not in all_content and "receipt" not in all_content and "agreement" not in all_content:
        score -= 1.0
        warnings.append("Evidence documents or payment receipt references are incomplete.")

    # Check 9: Signature
    if "signature" not in all_content and "undersigned" not in all_content and "sincerely" not in all_content:
        score -= 0.5
        warnings.append("Formal signature block is missing.")

    final_score = max(1.0, round(score, 1))
    return final_score, warnings


def draft_document_service(
    db: Session,
    case_id: str,
    doc_type: str,
    verified_matches: List[RetrievalMatch],
    case_facts: Dict[str, Any]
) -> DocumentResponseData:
    """Draft a structured legal document from verified sections and case facts."""
    if doc_type not in SUPPORTED_DOC_TYPES:
        doc_type = "legal_notice"

    verified_dicts = [m.model_dump() for m in verified_matches] if verified_matches else []

    ai_result = ai_client.fill_document_template(
        doc_type=doc_type,
        verified_sections=verified_dicts,
        case_facts=case_facts
    )

    title = ai_result.get("title") or f"{SUPPORTED_DOC_TYPES[doc_type]} - Ref: {case_id[:8]}"
    raw_sections = ai_result.get("sections", [])

    sections: List[DocumentSection] = []
    for sec in raw_sections:
        sections.append(DocumentSection(
            id=sec.get("id", "section"),
            title=sec.get("title", "Section"),
            content=sec.get("content", "")
        ))

    # Evaluate Quality Score
    quality_score, warnings = evaluate_document_quality(sections, case_facts)

    # Persist document to database
    doc_sections_dicts = [s.model_dump() for s in sections]
    doc = DocumentRepository.create_document(
        db=db,
        case_id=case_id,
        doc_type=doc_type,
        title=title,
        content_sections=doc_sections_dicts,
        disclaimer=MANDATORY_DISCLAIMER,
        quality_score=quality_score,
        quality_warnings=warnings
    )

    return DocumentResponseData(
        document_id=doc.id,
        case_id=doc.case_id,
        type=doc.type,
        title=doc.title,
        sections=sections,
        quality_score=doc.quality_score,
        quality_warnings=warnings,
        disclaimer=doc.disclaimer,
        created_at=doc.created_at.isoformat() + "Z"
    )
