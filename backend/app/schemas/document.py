"""Pydantic schemas for Document Drafting and Editing."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DocumentSection(BaseModel):
    id: str
    title: str
    content: str


class DocumentResponseData(BaseModel):
    document_id: str
    case_id: str
    type: str
    title: str
    sections: List[DocumentSection]
    quality_score: float = 8.0
    quality_warnings: List[str] = Field(default_factory=list)
    disclaimer: str
    created_at: str


class UpdateDocumentRequest(BaseModel):
    title: Optional[str] = None
    sections: List[DocumentSection]
