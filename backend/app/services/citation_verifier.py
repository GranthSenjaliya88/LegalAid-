"""
Citation Verifier Service (Phase 9).
Inspects generated legal output and verifies every citation against LegalAct, LegalSection, and retrieved sections set.
Removes or flags unsupported citations.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.legal.citation import extract_citations, verify_citation_against_db
from app.schemas.analysis import VerifyResponseData, VerificationItem
from app.schemas.legal import RetrievalMatch


def verify_generated_output(
    db: Session,
    generated_text: str,
    retrieved_matches: List[RetrievalMatch]
) -> VerifyResponseData:
    """Verify citations contained within generated text."""
    parsed_citations = extract_citations(generated_text)
    match_dicts = [m.model_dump() for m in retrieved_matches] if retrieved_matches else []

    items: List[VerificationItem] = []
    unsupported_count = 0
    verified_count = 0

    for cit in parsed_citations:
        res = verify_citation_against_db(db, cit, match_dicts)
        item = VerificationItem(
            citation_text=res["citation_text"],
            act_exists=res["act_exists"],
            section_exists=res["section_exists"],
            retrieved_in_case=res["retrieved_in_case"],
            text_matches=res["text_matches"],
            format_valid=res["format_valid"],
            is_valid=res["is_valid"],
            status_note=res["status_note"]
        )
        items.append(item)
        if item.is_valid:
            verified_count += 1
        else:
            unsupported_count += 1

    all_verified = len(items) > 0 and unsupported_count == 0

    return VerifyResponseData(
        all_verified=all_verified,
        total_citations=len(items),
        verified_count=verified_count,
        unsupported_count=unsupported_count,
        items=items
    )


def sanitize_unverified_claims(text: str, verification: VerifyResponseData) -> str:
    """Replace unsupported citations in text with 'Unable to verify this legal reference.'"""
    clean_text = text
    for item in verification.items:
        if not item.is_valid:
            clean_text = clean_text.replace(
                item.citation_text,
                f"{item.citation_text} [⚠️ Unable to verify this legal reference in database corpus]"
            )
    return clean_text
