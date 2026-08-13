"""
Phase 9 & 16 — Case Summary & Share With Lawyer Service.
Generates a structured, professional summary of the case for user review or advocate consultation.
Includes: Problem, Parties, Timeline, Jurisdiction, Amount, Applicable Laws, Evidence, and Uncertainties.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class CaseSummaryResponse(BaseModel):
    case_id: str
    problem_summary: str
    parties_involved: str
    jurisdiction_state: str
    incident_timeline: str
    disputed_amount: str
    applicable_laws: List[Dict[str, Any]]
    verified_citations: List[str]
    evidence_checklist: List[str]
    recommended_next_steps: List[str]
    uncertainties_and_gaps: Optional[str] = None
    lawyer_review_notice: str


def generate_case_summary_service(
    case_id: str,
    facts: Dict[str, Any],
    retrieved_matches: List[Any],
    next_steps: List[str]
) -> CaseSummaryResponse:
    """Generate structured Case Summary object suitable for PDF export or sharing with a lawyer."""
    incident = facts.get("incident") or "Issue described by user."
    parties = facts.get("parties") or "Complainant vs Respondent"
    state = facts.get("state") or "India"
    timeline = facts.get("date") or facts.get("incident_date") or "Recent"
    amount = facts.get("amount") or "Unspecified disputed amount"

    laws_list = []
    citations_list = []

    for m in retrieved_matches:
        laws_list.append({
            "act": m.act,
            "section": m.section,
            "title": m.title,
            "status": m.status or "CURRENT",
            "source_url": m.official_source_url or m.source_url
        })
        citations_list.append(f"{m.act} (Section {m.section})")

    evidence_summary = [
        "Written agreement / contract copy",
        "Payment receipts / transaction passbook",
        "Written notices / communications"
    ]

    uncertainty = None
    if not facts.get("state"):
        uncertainty = "State location is required to determine state rent control or labour rules."

    notice = (
        "CONFIDENTIAL CASE SUMMARY FOR LEGAL CONSULTATION. "
        "LegalAId is an AI decision-support platform and does not provide formal legal representation or legal advice. "
        "Please present this summary to a qualified advocate for legal counsel."
    )

    return CaseSummaryResponse(
        case_id=case_id,
        problem_summary=incident,
        parties_involved=parties,
        jurisdiction_state=state,
        incident_timeline=timeline,
        disputed_amount=amount,
        applicable_laws=laws_list,
        verified_citations=citations_list,
        evidence_checklist=evidence_summary,
        recommended_next_steps=next_steps or ["Issue a formal written notice.", "Consult a licensed advocate."],
        uncertainties_and_gaps=uncertainty,
        lawyer_review_notice=notice
    )
