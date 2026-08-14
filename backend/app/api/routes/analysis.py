"""
Analysis Pipeline Routes (Phases 5, 6, 7, 8, 9, 11).
Handles Classification, Database Retrieval, Clarification, Rights Explanation, Citation Verification, and Backend Orchestration.
"""

import re
import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.repositories import CaseRepository
from app.db.models import ClaimAuditLog, ExecutionTrace
from app.services.classifier import classify_case_service
from app.services.retriever import retrieve_legal_sections
from app.services.clarifier import evaluate_clarification, update_facts_from_answers
from app.services.explainer import explain_rights_service
from app.services.citation_verifier import verify_generated_output
from app.schemas.analysis import ClarifyRequestData
from app.legal.claim_citation import verify_claims_against_retrieved_corpus

from app.services.evidence_mapper import generate_evidence_checklist
from app.services.action_roadmap import generate_action_roadmap

router = APIRouter(prefix="/api/cases", tags=["analysis"])


# Fact fields carried through retrieval and explanation. Kept in one place so
# every phase works from the same complete set — this prevents facts (date,
# location, desired_outcome, additional_facts, …) from being silently dropped
# between clarification and re-retrieval.
_FACT_FIELDS = (
    "parties", "incident", "date", "incident_date", "location", "state",
    "city", "district", "amount", "agreement_exists", "notice_given",
    "notice_sent", "communications", "desired_outcome", "urgency",
    "additional_facts",
)


def _facts_to_dict(case) -> Dict[str, Any]:
    """Build the complete, clean fact dict for a case.

    Reads every known fact field (never SQLAlchemy internals) and applies
    case-level fallbacks for incident text, state, and subdomain. Every analysis
    phase uses this so no field is lost between clarification and re-retrieval.
    """
    facts = getattr(case, "facts", None)
    out: Dict[str, Any] = {}
    if facts is not None:
        for field in _FACT_FIELDS:
            out[field] = getattr(facts, field, None)
    # Fallbacks from the case row when the facts table is missing/blank.
    if not out.get("incident"):
        out["incident"] = case.original_text
    if not out.get("state") and getattr(case, "state", None):
        out["state"] = case.state
    # subdomain lives on the case row, not the facts table.
    out["subdomain"] = getattr(case, "subdomain", None)
    return out


@router.post("/{case_id}/classify", summary="Phase 5 - Classify Domain & Facts")
def classify_case_route(case_id: str, db: Session = Depends(get_db)):
    """
    Classify legal domain, subdomain, urgency, state, and extract structured facts.
    LLM is NOT allowed to decide section numbers at this step.
    """
    case = CaseRepository.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CASE_NOT_FOUND", "message": f"Case '{case_id}' not found."}
        )

    classify_res = classify_case_service(case.original_text)

    # Persist domain, subdomain, state, urgency & facts to DB
    CaseRepository.update_case_domain_and_status(
        db=db,
        case_id=case_id,
        domain=classify_res.domain,
        status="classified",
        subdomain=classify_res.subdomain,
        state=classify_res.facts.state,
        urgency=classify_res.urgency
    )
    CaseRepository.update_case_facts(db, case_id, classify_res.facts.model_dump())

    return {
        "success": True,
        "data": {
            "case_id": case.id,
            "domain": classify_res.domain,
            "subdomain": classify_res.subdomain,
            "confidence": classify_res.confidence,
            "jurisdiction_required": classify_res.jurisdiction_required,
            "urgency": classify_res.urgency,
            "facts": classify_res.facts.model_dump()
        }
    }


@router.post("/{case_id}/retrieve", summary="Phase 6 - Database Legal Retrieval")
def retrieve_case_route(case_id: str, db: Session = Depends(get_db)):
    """
    Search database corpus ONLY for matching statute sections.
    LLM is NEVER the source of truth for section numbers.
    """
    case = CaseRepository.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CASE_NOT_FOUND", "message": f"Case '{case_id}' not found."}
        )

    facts_dict = _facts_to_dict(case)

    retrieval_res = retrieve_legal_sections(domain=case.domain, facts=facts_dict)

    CaseRepository.update_case_domain_and_status(db, case_id, case.domain or "general", "retrieved")

    matches_list = [m.model_dump() for m in retrieval_res.matches]

    return {
        "success": True,
        "data": {
            "status": retrieval_res.status,
            "state_verified": retrieval_res.state_verified,
            "state_note": retrieval_res.state_note,
            "matches": matches_list
        }
    }


@router.post("/{case_id}/clarify", summary="Phase 7 - Clarification Check")
def clarify_case_route(case_id: str, db: Session = Depends(get_db)):
    """
    Determine if sufficient facts exist; generates up to 3 clarifying questions.
    """
    case = CaseRepository.get_case(db, case_id)
    if not case or not case.facts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CASE_NOT_FOUND", "message": f"Case '{case_id}' or facts not found."}
        )

    facts_data = _facts_to_dict(case)

    clarify_res = evaluate_clarification(facts_data, domain=case.domain)

    return {
        "success": True,
        "data": clarify_res.model_dump()
    }


@router.post("/{case_id}/clarify/respond", summary="Phase 7 - Clarification Response")
def clarify_respond_route(case_id: str, body: ClarifyRequestData, db: Session = Depends(get_db)):
    """
    Update CaseFacts with user answers and re-execute database retrieval.
    """
    case = CaseRepository.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CASE_NOT_FOUND", "message": f"Case '{case_id}' not found."}
        )

    current_facts = _facts_to_dict(case)

    updated_facts = update_facts_from_answers(current_facts, body.answers)
    CaseRepository.update_case_facts(db, case_id, updated_facts)

    CaseRepository.update_case_domain_and_status(
        db,
        case_id,
        case.domain or "general",
        "clarified",
        state=updated_facts.get("state") or case.state
    )

    # Re-retrieve with updated facts
    retrieval_res = retrieve_legal_sections(domain=case.domain, facts=updated_facts)
    matches_list = [m.model_dump() for m in retrieval_res.matches]

    return {
        "success": True,
        "data": {
            "status": "updated_and_retrieved",
            "state_verified": retrieval_res.state_verified,
            "state_note": retrieval_res.state_note,
            "matches": matches_list
        }
    }


@router.post("/{case_id}/explain", summary="Phase 8 - Rights Explanation")
def explain_case_route(case_id: str, db: Session = Depends(get_db)):
    """
    Generate user-friendly rights explanation strictly referencing retrieved database sections.
    """
    case = CaseRepository.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CASE_NOT_FOUND", "message": f"Case '{case_id}' not found."}
        )

    facts_dict = _facts_to_dict(case)

    retrieval_res = retrieve_legal_sections(domain=case.domain, facts=facts_dict)
    explain_res = explain_rights_service(
        matches=retrieval_res.matches,
        facts=facts_dict,
        language=case.language
    )

    CaseRepository.update_case_domain_and_status(db, case_id, case.domain or "general", "explained")

    return {
        "success": True,
        "data": explain_res.model_dump()
    }


@router.get("/{case_id}/evidence", summary="Evidence Mapper Checklist")
@router.post("/{case_id}/evidence", summary="Evidence Mapper Checklist")
def evidence_case_route(case_id: str, db: Session = Depends(get_db)):
    """Generate evidence suggestions checklist based on claim and domain."""
    case = CaseRepository.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CASE_NOT_FOUND", "message": f"Case '{case_id}' not found."}
        )

    facts_dict = _facts_to_dict(case)

    evidence_res = generate_evidence_checklist(
        domain=case.domain or "general",
        subdomain=case.subdomain,
        facts=facts_dict
    )

    return {
        "success": True,
        "data": evidence_res.model_dump()
    }


@router.get("/{case_id}/roadmap", summary="Action Roadmap (What You Can Do Next)")
@router.post("/{case_id}/roadmap", summary="Action Roadmap (What You Can Do Next)")
def roadmap_case_route(case_id: str, db: Session = Depends(get_db)):
    """Generate sequential action steps and urgency banner."""
    case = CaseRepository.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CASE_NOT_FOUND", "message": f"Case '{case_id}' not found."}
        )

    facts_dict = _facts_to_dict(case)

    roadmap_res = generate_action_roadmap(
        domain=case.domain or "general",
        subdomain=case.subdomain,
        urgency=case.urgency or "low",
        facts=facts_dict
    )

    return {
        "success": True,
        "data": roadmap_res.model_dump()
    }


@router.post("/{case_id}/verify", summary="Phase 9 - Citation Verifier")
def verify_case_route(case_id: str, db: Session = Depends(get_db)):
    """
    Inspect generated legal claims and verify every citation against LegalAct and LegalSection in DB.
    """
    case = CaseRepository.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CASE_NOT_FOUND", "message": f"Case '{case_id}' not found."}
        )

    facts_dict = _facts_to_dict(case)

    retrieval_res = retrieve_legal_sections(domain=case.domain, facts=facts_dict)
    explain_res = explain_rights_service(
        matches=retrieval_res.matches,
        facts=facts_dict,
        language=case.language
    )

    full_generated_text = f"{explain_res.summary}\n" + "\n".join([r.explanation for r in explain_res.rights])

    verify_res = verify_generated_output(
        db=db,
        generated_text=full_generated_text,
        retrieved_matches=retrieval_res.matches
    )

    return {
        "success": True,
        "data": verify_res.model_dump()
    }


@router.get("/{case_id}/summary", summary="Phase 9 & 16 - Case Summary & Share With Lawyer")
@router.post("/{case_id}/summary", summary="Phase 9 & 16 - Case Summary & Share With Lawyer")
def case_summary_route(case_id: str, db: Session = Depends(get_db)):
    """Generate structured Case Summary for user export or advocate consultation."""
    from app.services.case_summary import generate_case_summary_service
    case = CaseRepository.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CASE_NOT_FOUND", "message": f"Case '{case_id}' not found."}
        )

    facts_dict = _facts_to_dict(case)

    retrieval_res = retrieve_legal_sections(domain=case.domain, facts=facts_dict)
    summary_res = generate_case_summary_service(
        case_id=case.id,
        facts=facts_dict,
        retrieved_matches=retrieval_res.matches,
        next_steps=["Issue formal notice", "Lodge complaint on official portal", "Consult advocate"]
    )

    return {
        "success": True,
        "data": summary_res.model_dump()
    }


@router.post("/{case_id}/applicability", summary="Phase 7 & 16 - Legal Applicability Breakdown & Why This Law")
def case_applicability_route(case_id: str, db: Session = Depends(get_db)):
    """Evaluate detailed applicability breakdown for retrieved legal provisions against case facts."""
    from app.legal.applicability import evaluate_provision_applicability
    case = CaseRepository.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CASE_NOT_FOUND", "message": f"Case '{case_id}' not found."}
        )

    facts_dict = _facts_to_dict(case)
    facts_dict["domain"] = case.domain

    retrieval_res = retrieve_legal_sections(domain=case.domain, facts=facts_dict)
    evaluations = [evaluate_provision_applicability(m, facts_dict).model_dump() for m in retrieval_res.matches]

    return {
        "success": True,
        "data": {
            "case_id": case.id,
            "evaluations": evaluations
        }
    }


@router.post("/{case_id}/compare", summary="Phase 17 - Compare Candidate Laws")
def case_compare_route(case_id: str, db: Session = Depends(get_db)):
    """Generate side-by-side comparison table of candidate laws explaining why they apply or do not apply."""
    from app.legal.applicability import generate_law_comparison_matrix
    case = CaseRepository.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CASE_NOT_FOUND", "message": f"Case '{case_id}' not found."}
        )

    facts_dict = _facts_to_dict(case)
    facts_dict["domain"] = case.domain

    retrieval_res = retrieve_legal_sections(domain=case.domain, facts=facts_dict)
    comparison_rows = generate_law_comparison_matrix(retrieval_res.matches, facts_dict)

    return {
        "success": True,
        "data": {
            "case_id": case.id,
            "rows": [r.model_dump() for r in comparison_rows]
        }
    }


@router.post("/{case_id}/analyze", summary="Phase 11 - Unified Case Orchestration")
def analyze_case_orchestration_route(case_id: str, db: Session = Depends(get_db)):
    """
    Unified end-to-end backend orchestration pipeline (Phase 11).
    Orchestrates Classification -> Fact Extraction -> Clarification -> Retrieval -> Explanation -> Evidence -> Action Roadmap.
    Returns deterministic status: complete | needs_clarification | insufficient_information | error.
    Also persists claim audit logs and execution traces for full pipeline traceability.
    """
    case = CaseRepository.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CASE_NOT_FOUND", "message": f"Case '{case_id}' not found."}
        )

    # 0. Nonsense / unintelligible input guard.
    # A meaningful legal query must have at least 3 words and contain at least one
    # recognisable alphabetic word (length >= 3).  Pure gibberish like "xyzqwerty999"
    # should return insufficient_information rather than trigger clarification.
    original_text = case.original_text or ""
    meaningful_words = [w for w in re.split(r"\s+", original_text.strip()) if re.search(r"[a-zA-Z\u0900-\u097F]{3,}", w)]
    if len(meaningful_words) < 3 and not case.facts:
        # Persist an execution trace so this refusal is traceable
        _persist_execution_trace(
            db, case_id,
            user_input=original_text,
            language=case.language,
            stage="insufficient_information",
            payload={"reason": "Unintelligible or too-short input", "word_count": len(meaningful_words)}
        )
        return {
            "success": True,
            "data": {
                "status": "insufficient_information",
                "case_id": case.id,
                "domain": None,
                "subdomain": None,
                "facts": {},
                "clarification": None,
                "explain": None,
                "evidence": None,
                "roadmap": None,
                "message": "We couldn't identify a legal situation from the provided text. Please describe your legal problem in more detail."
            }
        }

    # 1. Classification & Fact Extraction (if not yet performed)
    if not case.facts or case.status == "received":
        classify_res = classify_case_service(case.original_text)
        CaseRepository.update_case_domain_and_status(
            db=db,
            case_id=case_id,
            domain=classify_res.domain,
            status="classified",
            subdomain=classify_res.subdomain,
            state=classify_res.facts.state,
            urgency=classify_res.urgency
        )
        CaseRepository.update_case_facts(db, case_id, classify_res.facts.model_dump())
        # Refresh case instance
        case = CaseRepository.get_case(db, case_id)

    facts_dict = _facts_to_dict(case)
    if not facts_dict.get("domain") and case.domain:
        facts_dict["domain"] = case.domain

    # 2. Clarification Evaluation
    clarify_res = evaluate_clarification(facts_dict, domain=case.domain)

    # If critical information is missing and case hasn't been clarified yet, pause for clarification
    if clarify_res.needs_clarification and clarify_res.questions and case.status not in ("clarified", "explained"):
        _persist_execution_trace(
            db, case_id,
            user_input=original_text,
            language=case.language,
            stage="needs_clarification",
            payload={"questions": clarify_res.questions, "missing_facts": clarify_res.missing_facts}
        )
        return {
            "success": True,
            "data": {
                "status": "needs_clarification",
                "case_id": case.id,
                "domain": case.domain,
                "subdomain": case.subdomain,
                "facts": facts_dict,
                "clarification": clarify_res.model_dump(),
                "explain": None,
                "evidence": None,
                "roadmap": None,
                "message": "Clarification required to refine legal applicability."
            }
        }

    # 3. Database Legal Retrieval
    retrieval_res = retrieve_legal_sections(domain=case.domain, facts=facts_dict)
    CaseRepository.update_case_domain_and_status(db, case_id, case.domain or "general", "retrieved")

    # 4. Rights Explanation
    explain_res = explain_rights_service(
        matches=retrieval_res.matches,
        facts=facts_dict,
        language=case.language
    )

    # 5. Evidence Suggestions
    evidence_res = generate_evidence_checklist(
        domain=case.domain or "general",
        subdomain=case.subdomain,
        facts=facts_dict
    )

    # 6. Action Roadmap
    roadmap_res = generate_action_roadmap(
        domain=case.domain or "general",
        subdomain=case.subdomain,
        urgency=case.urgency or "low",
        facts=facts_dict
    )

    # 7. Final Status Determination
    if not retrieval_res.matches or explain_res.confidence == "INSUFFICIENT INFORMATION":
        status_str = "insufficient_information"
    else:
        status_str = "complete"

    CaseRepository.update_case_domain_and_status(db, case_id, case.domain or "general", "explained")

    # 8. Persist claim audit logs — every claim gets its own row in claim_audit_logs.
    #    The explainer already verified claims internally; we surface those records here.
    _persist_claim_audit_logs(db, case_id, retrieval_res.matches, explain_res)

    # 9. Persist a full execution trace for audit and debugging.
    _persist_execution_trace(
        db, case_id,
        user_input=original_text,
        language=case.language,
        stage=status_str,
        payload={
            "domain": case.domain,
            "subdomain": case.subdomain,
            "facts": facts_dict,
            "retrieved_count": len(retrieval_res.matches),
            "confidence": explain_res.confidence,
            "rights_count": len(explain_res.rights),
        }
    )

    return {
        "success": True,
        "data": {
            "status": status_str,
            "case_id": case.id,
            "domain": case.domain,
            "subdomain": case.subdomain,
            "facts": facts_dict,
            "clarification": clarify_res.model_dump(),
            "explain": explain_res.model_dump(),
            "evidence": evidence_res.model_dump(),
            "roadmap": roadmap_res.model_dump(),
            "message": "Case analysis completed successfully." if status_str == "complete" else "No matching statutory provisions found with sufficient confidence."
        }
    }


# ---------------------------------------------------------------------------
# Private helpers for audit persistence
# ---------------------------------------------------------------------------

def _persist_claim_audit_logs(db: Session, case_id: str, matches, explain_res) -> None:
    """Persist per-claim audit rows derived from the explanation result.

    Extracts claims from rights items, verifies them against retrieved matches,
    and writes one ClaimAuditLog row per claim.  Safe to call even when there
    are zero matches or zero rights — it simply writes nothing in that case.
    """
    try:
        claim_texts = [
            item.explanation
            for item in (explain_res.rights or [])
            if item.explanation
        ]
        if not claim_texts:
            return

        claim_result = verify_claims_against_retrieved_corpus(claim_texts, matches)
        for item in claim_result.claims:
            log = ClaimAuditLog(
                case_id=case_id,
                claim_id=item.claim_id,
                claim_text=item.claim_text[:2000],  # guard against very long text
                source_act=item.source_act,
                source_section=item.source_section,
                source_url=item.source_url,
                support_level=item.support_level,
                verification_status=item.verification_status,
            )
            db.add(log)
        db.commit()
    except Exception as exc:
        # Audit persistence must never crash the user-facing pipeline.
        db.rollback()
        from app.core.logging import logger
        logger.warning("[audit] Failed to persist claim audit logs for case %s: %s", case_id, exc)


def _persist_execution_trace(
    db: Session,
    case_id: str,
    user_input: str,
    language: str,
    stage: str,
    payload: Dict[str, Any],
) -> None:
    """Persist a single execution trace record for this pipeline run."""
    try:
        trace = ExecutionTrace(
            case_id=case_id,
            stage=stage,
            payload=json.dumps({
                "user_input": user_input[:500],  # avoid huge blobs
                "language": language,
                **payload
            }, default=str),
        )
        db.add(trace)
        db.commit()
    except Exception as exc:
        db.rollback()
        from app.core.logging import logger
        logger.warning("[trace] Failed to persist execution trace for case %s: %s", case_id, exc)
