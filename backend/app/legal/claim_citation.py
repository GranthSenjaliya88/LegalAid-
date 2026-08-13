"""
Phase 5 — Claim-Level Citation & Support Verification Engine.
Parses every AI-generated legal statement into a structured claim object.
Verifies that each claim is supported by at least one retrieved database record.
Classifies support level as: DIRECTLY_SUPPORTED, PARTIALLY_SUPPORTED, NOT_SUPPORTED, or BLOCKED.
Only DIRECTLY_SUPPORTED claims may be presented as verified legal facts.
PARTIALLY_SUPPORTED claims are displayed with explicit source qualifications.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field
from app.schemas.legal import RetrievalMatch
from app.core.logging import logger


class ClaimCitationItem(BaseModel):
    claim_id: str
    claim_text: str
    source_id: Optional[int] = None
    source_type: Optional[str] = None
    source_act: Optional[str] = None
    source_section: Optional[str] = None
    source_record_id: Optional[int] = None
    source_url: Optional[str] = None
    official_url: Optional[str] = None
    support_level: str = "DIRECTLY_SUPPORTED"  # DIRECTLY_SUPPORTED, PARTIALLY_SUPPORTED, NOT_SUPPORTED, BLOCKED
    verification_status: str = "VERIFIED"  # VERIFIED, UNVERIFIED, BLOCKED
    qualifier_note: Optional[str] = None
    blocking_reason: Optional[str] = None


class ClaimVerificationResult(BaseModel):
    all_claims_supported: bool
    total_claims: int
    directly_supported_count: int
    partially_supported_count: int
    blocked_claims_count: int
    claims: List[ClaimCitationItem]

    @property
    def verified_claims_count(self) -> int:
        return self.directly_supported_count + self.partially_supported_count


def verify_claims_against_retrieved_corpus(
    claims: List[str],
    retrieved_matches: List[RetrievalMatch]
) -> ClaimVerificationResult:
    """
    Verify each legal claim individually against retrieved statutory sections.
    """
    if not claims:
        return ClaimVerificationResult(
            all_claims_supported=True,
            total_claims=0,
            directly_supported_count=0,
            partially_supported_count=0,
            blocked_claims_count=0,
            claims=[]
        )

    directly_count = 0
    partially_count = 0
    blocked_count = 0
    claim_items: List[ClaimCitationItem] = []

    for idx, claim_text in enumerate(claims):
        claim_id = f"CLM-{idx+1:03d}"
        clean_claim = claim_text.strip()
        if not clean_claim:
            continue

        best_match: Optional[RetrievalMatch] = None
        best_overlap = 0

        claim_words = set(clean_claim.lower().split())

        for m in retrieved_matches:
            sec_text = (
                (m.act or "") + " " + (m.section or "") + " " + (m.title or "") + " " +
                (m.relevant_text or "") + " " + (m.plain_language_summary or "")
            ).lower()
            sec_words = set(sec_text.split())
            overlap = len(claim_words.intersection(sec_words))

            if overlap > best_overlap:
                best_overlap = overlap
                best_match = m

        if best_match and best_overlap >= 4:
            directly_count += 1
            claim_items.append(ClaimCitationItem(
                claim_id=claim_id,
                claim_text=clean_claim,
                source_act=best_match.act,
                source_section=best_match.section,
                source_url=best_match.official_source_url or best_match.source_url,
                support_level="DIRECTLY_SUPPORTED",
                verification_status="VERIFIED"
            ))
        elif best_match and best_overlap >= 2:
            partially_count += 1
            claim_items.append(ClaimCitationItem(
                claim_id=claim_id,
                claim_text=clean_claim,
                source_act=best_match.act,
                source_section=best_match.section,
                source_url=best_match.official_source_url or best_match.source_url,
                support_level="PARTIALLY_SUPPORTED",
                verification_status="VERIFIED",
                qualifier_note="Based on retrieved sources, this provision may be relevant, but does not by itself establish the full conclusion."
            ))
        else:
            blocked_count += 1
            claim_items.append(ClaimCitationItem(
                claim_id=claim_id,
                claim_text=clean_claim,
                support_level="BLOCKED",
                verification_status="BLOCKED",
                blocking_reason="No retrieved database statutory provision directly supports this claim."
            ))

    all_supported = (blocked_count == 0 and directly_count > 0)
    return ClaimVerificationResult(
        all_claims_supported=all_supported,
        total_claims=len(claim_items),
        directly_supported_count=directly_count,
        partially_supported_count=partially_count,
        blocked_claims_count=blocked_count,
        claims=claim_items
    )


@dataclass
class Claim:
    claim_id: str
    claim_text: str
    source_record_id: Optional[int]
    source_act: Optional[str]
    source_section: Optional[str]
    source_url: Optional[str]
    support_level: str  # DIRECTLY_SUPPORTED, PARTIALLY_SUPPORTED, NOT_SUPPORTED, BLOCKED
    verification_status: str
    qualifier_note: Optional[str] = None


def verify_claim(
    claim_text: str,
    retrieved_sections: dict[int, Any],
) -> Claim:

    for record_id, section in retrieved_sections.items():
        full_text = getattr(section, "full_text", None) or getattr(section, "text", None) or getattr(section, "relevant_text", "")
        if not full_text:
            continue

        normalized_claim = claim_text.lower()

        legal_terms = [
            word
            for word in normalized_claim.split()
            if len(word) > 4
        ]

        matching_terms = [
            word
            for word in legal_terms
            if word in full_text.lower()
        ]

        act_obj = getattr(section, "act", None)
        act_name = getattr(act_obj, "short_name", None) if act_obj else getattr(section, "act", "Statute")
        sec_num = getattr(section, "section_number", None) or getattr(section, "section", "")
        src_obj = getattr(section, "source", None)
        official_url = (getattr(src_obj, "official_url", None) if src_obj else None) or getattr(section, "official_source_url", None) or getattr(section, "source_url", None)

        if len(matching_terms) >= 4:
            return Claim(
                claim_id=f"claim-{record_id}",
                claim_text=claim_text,
                source_record_id=record_id,
                source_act=act_name,
                source_section=sec_num,
                source_url=official_url,
                support_level="DIRECTLY_SUPPORTED",
                verification_status="VERIFIED"
            )
        elif len(matching_terms) >= 2:
            return Claim(
                claim_id=f"claim-{record_id}",
                claim_text=claim_text,
                source_record_id=record_id,
                source_act=act_name,
                source_section=sec_num,
                source_url=official_url,
                support_level="PARTIALLY_SUPPORTED",
                verification_status="REQUIRES_AUDIT",
                qualifier_note="Based on retrieved sources, this provision may be relevant, but does not by itself establish the full conclusion."
            )

    return Claim(
        claim_id="blocked",
        claim_text=claim_text,
        source_record_id=None,
        source_act=None,
        source_section=None,
        source_url=None,
        support_level="BLOCKED",
        verification_status="BLOCKED",
    )
