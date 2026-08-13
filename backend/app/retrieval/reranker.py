"""
Deterministic Legal Reranker Module for LegalAId.
Reranks candidate legal provisions using transparent, testable, deterministic scoring components.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ScoringFactors:
    rrf_score: float
    concept_match: float
    domain_match: float
    subdomain_match: float
    state_match: float
    status_score: float
    authority_priority_score: float
    total_score: float
    reason: str


def compute_deterministic_score(
    candidate: Dict[str, Any],
    query_concepts: List[str],
    target_domain: Optional[str] = None,
    target_subdomain: Optional[str] = None,
    user_state: Optional[str] = None,
    user_city: Optional[str] = None
) -> ScoringFactors:
    """
    Calculate deterministic relevance score for a candidate legal provision.
    """
    rrf_score = float(candidate.get("fusion_score", candidate.get("score", 0.0)))
    
    # 1. Concept match (+0.25)
    cand_text = (
        str(candidate.get("title", "")) + " " +
        str(candidate.get("full_text", candidate.get("relevant_text", ""))) + " " +
        str(candidate.get("keywords", ""))
    ).lower()
    
    concept_match = 0.0
    matched_concepts = []
    for concept in query_concepts:
        if concept.lower() in cand_text:
            concept_match = 0.25
            matched_concepts.append(concept)
            break

    # 2. Domain & Subdomain match (+0.20 & +0.10)
    cand_domain = str(candidate.get("domain", "")).lower()
    cand_subdomain = str(candidate.get("subdomain", "")).lower()
    
    domain_match = 0.0
    if target_domain and cand_domain == target_domain.lower():
        domain_match = 0.20

    subdomain_match = 0.0
    if target_subdomain and cand_subdomain == target_subdomain.lower():
        subdomain_match = 0.10

    # 3. State Jurisdiction match (+0.15)
    cand_state = str(candidate.get("state", "All")).lower()
    state_match = 0.0
    if not user_state or user_state.lower() == "all" or cand_state == "all":
        state_match = 0.15
    elif cand_state == user_state.lower():
        state_match = 0.15

    # 4. Current Law Status (+0.15)
    status_str = str(candidate.get("status", "CURRENT")).upper()
    status_score = 0.15 if status_str in {"CURRENT", "ACTIVE"} else 0.0

    # 5. Source Authority Priority (+0.15 for Priority Level 1/2)
    priority = int(candidate.get("priority_level", 1))
    authority_priority_score = max(0.0, 0.15 - (priority - 1) * 0.04)

    total_score = (
        rrf_score +
        concept_match +
        domain_match +
        subdomain_match +
        state_match +
        status_score +
        authority_priority_score
    )

    reasons = []
    if concept_match > 0:
        reasons.append(f"Matched legal concepts: {', '.join(matched_concepts)}")
    if domain_match > 0:
        reasons.append(f"Domain match: {target_domain}")
    if state_match > 0:
        reasons.append(f"Jurisdiction match: {user_state or 'India-wide'}")
    if status_score > 0:
        reasons.append("Current active statutory law")

    reason_summary = "; ".join(reasons) if reasons else "General statutory relevance match."

    return ScoringFactors(
        rrf_score=rrf_score,
        concept_match=concept_match,
        domain_match=domain_match,
        subdomain_match=subdomain_match,
        state_match=state_match,
        status_score=status_score,
        authority_priority_score=authority_priority_score,
        total_score=total_score,
        reason=reason_summary
    )


def rerank_candidates(
    candidates: List[Dict[str, Any]],
    query_concepts: List[str],
    target_domain: Optional[str] = None,
    target_subdomain: Optional[str] = None,
    user_state: Optional[str] = None,
    user_city: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Rerank list of candidate records deterministically based on structured legal factors.
    """
    scored = []
    for cand in candidates:
        sf = compute_deterministic_score(
            candidate=cand,
            query_concepts=query_concepts,
            target_domain=target_domain,
            target_subdomain=target_subdomain,
            user_state=user_state,
            user_city=user_city
        )
        cand_copy = dict(cand)
        cand_copy["rerank_score"] = sf.total_score
        cand_copy["rerank_reason"] = sf.reason
        scored.append(cand_copy)

    scored.sort(key=lambda x: x["rerank_score"], reverse=True)
    return scored
