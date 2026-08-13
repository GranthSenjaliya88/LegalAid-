"""Pydantic schemas for classification, clarification, rights explanation, and citation verification."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.case import CaseFactsData
from app.schemas.legal import RetrievalMatch


class ClassifyResponseData(BaseModel):
    domain: str
    subdomain: Optional[str] = None
    confidence: float = 1.0
    jurisdiction_required: bool = False
    urgency: str = "low"  # low, medium, high, urgent
    facts: CaseFactsData


class ClarifyRequestData(BaseModel):
    answers: Dict[str, Any] = Field(default_factory=dict, description="Key-value answers to missing facts questions")


class ClarifyResponseData(BaseModel):
    needs_clarification: bool
    questions: List[str] = Field(default_factory=list, description="Up to 3 clarifying questions")
    missing_facts: List[str] = Field(default_factory=list)


class CitationDetail(BaseModel):
    act: str
    section: str
    source_reference: Optional[str] = None


class RightExplanationItem(BaseModel):
    explanation: str
    why_applies: Optional[str] = None
    citations: List[CitationDetail]


class ExplainResponseData(BaseModel):
    summary: str
    what_we_understood: Optional[str] = None
    possible_rights: List[str] = Field(default_factory=list)
    relevant_law: List[Dict[str, Any]] = Field(default_factory=list)
    what_is_uncertain: Optional[str] = None
    documents_that_may_help: List[str] = Field(default_factory=list)
    rights: List[RightExplanationItem] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    reasoning_map: List[Dict[str, Any]] = Field(default_factory=list, description="Phase 1: 10-step auditable Legal Reasoning Map")
    why_this_law: List[Dict[str, Any]] = Field(default_factory=list, description="Phase 2: Why This Law May Apply breakdown")
    why_not_this_law: List[Dict[str, Any]] = Field(default_factory=list, description="Phase 2: Other Laws Considered and Excluded breakdown")
    emergency_plan: Optional[Dict[str, Any]] = Field(default=None, description="Phase 7: Urgent Action Mode Plan")
    verification_card: Optional[Dict[str, Any]] = Field(default=None, description="Phase 13: UI Trust Verification Card")
    law_comparison_table: List[Dict[str, Any]] = Field(default_factory=list, description="Phase 14: Law Comparison Table")
    confidence: str = "HIGH"  # HIGH, MEDIUM, LOW, INSUFFICIENT INFORMATION
    disclaimer: Optional[str] = "This is general legal information, not legal advice."


class EvidenceItem(BaseModel):
    document_name: str
    importance: str  # "essential", "supporting"
    why_it_matters: str
    available: bool = False


class EvidenceResponseData(BaseModel):
    claim_summary: str
    checklist: List[EvidenceItem]


class ActionStepItem(BaseModel):
    step_number: int
    title: str
    description: str
    required_document: Optional[str] = None
    next_action: Optional[str] = None


class ActionRoadmapResponseData(BaseModel):
    urgency: str
    urgent_warning: Optional[str] = None
    steps: List[ActionStepItem]


class VerificationItem(BaseModel):
    citation_text: str
    act_exists: bool
    section_exists: bool
    retrieved_in_case: bool
    text_matches: bool
    format_valid: bool
    is_valid: bool
    status_note: str


class VerifyResponseData(BaseModel):
    all_verified: bool
    total_citations: int
    verified_count: int
    unsupported_count: int
    items: List[VerificationItem]
