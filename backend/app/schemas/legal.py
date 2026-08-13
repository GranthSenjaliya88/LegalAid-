"""Pydantic schemas for Legal Corpus and Statute Retrieval."""

from typing import Optional, List
from pydantic import BaseModel, Field


class LegalActOut(BaseModel):
    id: int
    name: str
    short_name: str
    year: int
    jurisdiction: str
    domain: str
    source: Optional[str] = None
    version: str
    created_at: str


class LegalSectionOut(BaseModel):
    id: int
    act_id: int
    act_short_name: Optional[str] = None
    section_number: str
    title: Optional[str] = None
    text: str
    domain: str
    language: str
    source_reference: Optional[str] = None
    created_at: str


class RetrievalMatch(BaseModel):
    act: str
    section: str
    title: Optional[str] = None
    relevant_text: str
    plain_language_summary: Optional[str] = None
    confidence: float
    source_reference: Optional[str] = None
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    official_source_url: Optional[str] = None
    source_authority: Optional[str] = None
    source_type: Optional[str] = None
    historical_reference: Optional[str] = None
    state: Optional[str] = "All"
    domain: Optional[str] = "general"
    status: Optional[str] = "CURRENT"
    last_verified: Optional[str] = None
    why_applies: Optional[str] = None


class RetrievalResponseData(BaseModel):
    status: str  # "success" or "insufficient_confidence"
    matches: List[RetrievalMatch]
    state_verified: bool = True
    state_note: Optional[str] = None


class IntakeRequest(BaseModel):
    text: str = Field(min_length=10, max_length=10000)
    language: Optional[str] = None


class CaseAnalysisResponse(BaseModel):
    case_id: int
    language: str
    domain: str
    subdomain: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    incident_date: Optional[str] = None

    confidence: str

    facts: dict
    missing_information: list[str]

    legal_sources: list[dict]

    rights: list[dict]

    evidence: list[dict]

    action_steps: list[dict]

    blocked_claims: list[str]

