"""
Pydantic schemas for the LegalAId API.

These define the shape of every request and response body.
Downstream steps (classifier, retriever, explainer …) import
these types so the contract is enforced end-to-end.
"""

from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field


# ─────────────────────────────────────────── Acts ──────────────────────────

class ActBase(BaseModel):
    name: str
    short_name: str
    year: int
    domain: str
    description: Optional[str] = None
    source_url: Optional[str] = None


class ActOut(ActBase):
    id: int
    is_active: int
    section_count: int = 0
    created_at: str

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────── Sections ─────────────────────

class SectionBase(BaseModel):
    section_number: str
    title: Optional[str] = None
    text: str
    domain: str
    keywords: list[str] = Field(default_factory=list)


class SectionOut(SectionBase):
    id: int
    act_id: int
    act_short_name: str
    is_active: int
    created_at: str
    # embedding_json is intentionally excluded from public API

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────── Search ───────────────────────

class SearchResult(BaseModel):
    section_id: int
    act_id: int
    act_short_name: str
    section_number: str
    title: Optional[str]
    text: str
    domain: str
    keywords: list[str]
    bm25_score: float = Field(description="BM25 relevance score — lower is more relevant in SQLite FTS5")


class SearchResponse(BaseModel):
    query: str
    domain_filter: Optional[str]
    total: int
    results: list[SearchResult]


# ──────────────────────────────────────────── Health ───────────────────────

class CorpusStats(BaseModel):
    acts_count: int
    sections_count: int
    fts_index_count: int
    domains: dict[str, int]   # domain → section count


class HealthResponse(BaseModel):
    status: str
    version: str
    corpus: CorpusStats


# ──────────────────────────────────────────── Verify ───────────────────────

class VerifyIssue(BaseModel):
    check: str
    severity: str   # "error" | "warning"
    detail: str


class VerifyResponse(BaseModel):
    passed: bool
    issues: list[VerifyIssue]
    summary: str


# ──────────────────────────────────────────── Step 2: Classifier ────────────

class ExtractedFacts(BaseModel):
    """Structured facts extracted from the user's free-form description."""
    parties: Optional[str] = Field(None, description="Who is involved (e.g. 'user and landlord')")
    dates: Optional[str]   = Field(None, description="Any dates or time periods mentioned")
    amounts: Optional[str] = Field(None, description="Any money amounts mentioned")
    issue_summary: Optional[str] = Field(None, description="One-sentence plain description of what happened")
    user_goal: Optional[str]     = Field(None, description="What the user wants: refund, compensation, notice, etc.")


class ClassifierOutput(BaseModel):
    """Output of the Classifier Agent (Step 2)."""
    classified_domain: str = Field(
        ...,
        description="Legal domain: consumer | labor | tenant | other",
        pattern=r"^(consumer|labor|tenant|other)$",
    )
    extracted_facts: ExtractedFacts


# ──────────────────────────────────────────── Step 2: Case session ──────────

class CaseMessage(BaseModel):
    """Request body for POST /case/{id}/message."""
    text: str = Field(..., min_length=1, max_length=4000,
                      description="Free-form description of the legal situation (Hindi or English)")


class CreateCaseResponse(BaseModel):
    """Response body for POST /case."""
    case_id: str


class UpdateFactsRequest(BaseModel):
    """Request body for PATCH /case/{case_id}/facts."""
    classified_domain: Optional[str] = Field(
        None,
        description="Updated legal domain: consumer | labor | tenant | other",
        pattern=r"^(consumer|labor|tenant|other)$",
    )
    extracted_facts: Optional[ExtractedFacts] = None


# ──────────────────────────────────────────── Steps 3-8: Pipeline Schemas ────

class RetrievedSection(BaseModel):
    section_id: int
    act_short_name: str
    act_name: str
    section_number: str
    title: Optional[str]
    text: str
    domain: str
    score: float


class RetrievalOutput(BaseModel):
    query_used: str
    domain_filter: Optional[str]
    total_found: int
    sections: list[RetrievedSection]


class ClarificationOutput(BaseModel):
    needs_clarification: bool
    question: Optional[str] = None
    missing_fields: list[str] = Field(default_factory=list)


class ExplanationOutput(BaseModel):
    plain_explanation: str
    cited_sections: list[str]
    key_rights: list[str]


class DraftDocumentOutput(BaseModel):
    document_type: str  # e.g. "Legal Notice", "Consumer Complaint"
    title: str
    content: str
    sections_referenced: list[str]


class CitationVerification(BaseModel):
    citation_text: str
    section_number: str
    act_short_name: str
    is_valid: bool
    db_section_id: Optional[int] = None
    detail: str


class VerificationResult(BaseModel):
    all_citations_valid: bool
    total_citations: int
    verified_citations: int
    citations: list[CitationVerification]


class CaseState(BaseModel):
    """Full case state — returned by GET /case/{id} and pipeline endpoints."""
    case_id: str
    created_at: str
    step: str   # awaiting_input | classified | retrieved | explained | drafted | completed
    messages: list[dict[str, Any]]
    classifier_output: Optional[ClassifierOutput] = None
    retrieval_output: Optional[RetrievalOutput] = None
    clarification_output: Optional[ClarificationOutput] = None
    explanation_output: Optional[ExplanationOutput] = None
    draft_output: Optional[DraftDocumentOutput] = None
    verification_result: Optional[VerificationResult] = None


# ──────────────────────────────────────────── New Platform Schemas ───────────

class EvidenceItemSchema(BaseModel):
    item_id: str
    title: str
    description: str
    category: str
    importance: str  # CRITICAL, RECOMMENDED, OPTIONAL
    status: str  # Available, Missing, Not Applicable


class EvidencePackSchema(BaseModel):
    case_id: str
    domain: str
    checklist: list[EvidenceItemSchema]
    completion_percentage: float
    missing_critical_count: int


class LawComparisonRowSchema(BaseModel):
    law_title: str
    status: str
    applicability: str
    reason: str


class LawComparisonMatrixSchema(BaseModel):
    case_id: Optional[str] = None
    rows: list[LawComparisonRowSchema]


class OfficialAuthoritySchema(BaseModel):
    id: int
    name: str
    domain: str
    jurisdiction: str
    purpose: str
    who_can_use: Optional[str] = None
    helpline: Optional[str] = None
    official_portal: Optional[str] = None
    online_filing_url: Optional[str] = None
    source_url: Optional[str] = None
    verification_status: str


class OfficialProcedureSchema(BaseModel):
    id: int
    domain: str
    subdomain: Optional[str] = None
    problem_title: str
    right_summary: str
    authority_name: str
    procedure_steps: list[str]
    required_documents: list[str]
    official_portal_url: Optional[str] = None
    follow_up_timeline: Optional[str] = None
    source_url: Optional[str] = None
    verification_status: str


class SourceRegistrySchema(BaseModel):
    id: int
    authority: str
    source_type: str
    title: str
    url: Optional[str] = None
    publication_date: Optional[str] = None
    retrieved_at: Optional[str] = None
    content_hash: Optional[str] = None
    verification_status: str


class DataQualityDashboardSchema(BaseModel):
    total_acts: int
    total_sections: int
    total_rules: int
    total_regulations: int
    total_notifications: int
    total_judgments: int
    total_authorities: int
    total_procedures: int
    total_concepts: int
    current_sections: int
    historical_sections: int
    domains_count: int
    domains_covered: dict[str, int]
    states_count: int
    states_covered: dict[str, int]
    sections_without_official_source: int
    acts_with_official_source: int
    integrity_passed: bool
    integrity_summary: str

