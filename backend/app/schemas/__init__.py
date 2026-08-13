"""API schemas package."""

from app.schemas.case import (
    CreateCaseRequest,
    CreateCaseResponseData,
    CaseFactsData,
    CaseStateData
)
from app.schemas.legal import (
    LegalActOut,
    LegalSectionOut,
    RetrievalMatch,
    RetrievalResponseData
)
from app.schemas.analysis import (
    ClassifyResponseData,
    ClarifyRequestData,
    ClarifyResponseData,
    ExplainResponseData,
    VerifyResponseData
)
from app.schemas.document import (
    DocumentSection,
    DocumentResponseData,
    UpdateDocumentRequest
)
from pydantic import BaseModel, Field
from typing import Optional, List

class ActOut(BaseModel):
    id: int
    name: str
    short_name: str
    year: int
    domain: str
    description: Optional[str] = None
    source_url: Optional[str] = None
    is_active: int = 1
    section_count: int = 0
    created_at: Optional[str] = None

class SectionOut(BaseModel):
    id: int
    act_id: int
    act_short_name: str
    section_number: str
    title: Optional[str] = None
    text: str
    domain: str
    keywords: List[str] = Field(default_factory=list)
    is_active: int = 1
    created_at: Optional[str] = None

class SearchResult(BaseModel):
    section_id: int
    act_id: int
    act_short_name: str
    section_number: str
    title: Optional[str] = None
    text: str
    domain: str
    keywords: List[str] = Field(default_factory=list)
    bm25_score: float = 0.0

class SearchResponse(BaseModel):
    query: str
    domain_filter: Optional[str] = None
    total: int
    results: List[SearchResult]

class VerifyIssue(BaseModel):
    check: str
    severity: str
    detail: str

class VerifyResponse(BaseModel):
    passed: bool
    issues: List[VerifyIssue] = Field(default_factory=list)
    summary: str = ""
