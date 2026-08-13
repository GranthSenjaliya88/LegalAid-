"""Pydantic schemas for Case intake and session status."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class CreateCaseRequest(BaseModel):
    text: str = Field(..., min_length=1, description="User's legal problem description (Hindi or English)")
    language: str = Field(default="en", description="Language code: 'en' or 'hi'")
    session_id: Optional[str] = Field(None, description="Optional session tracking identifier")


class CreateCaseResponseData(BaseModel):
    case_id: str
    language: str
    status: str


class CaseFactsData(BaseModel):
    parties: Optional[str] = None
    incident: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    state: Optional[str] = None
    subdomain: Optional[str] = None
    amount: Optional[str] = None
    agreement_exists: Optional[bool] = None
    notice_given: Optional[bool] = None
    desired_outcome: Optional[str] = None
    urgency: Optional[str] = "low"
    additional_facts: Optional[Dict[str, Any]] = None


class CaseStateData(BaseModel):
    case_id: str
    session_id: Optional[str] = None
    language: str
    original_text: str
    domain: Optional[str] = None
    subdomain: Optional[str] = None
    state: Optional[str] = None
    urgency: Optional[str] = "low"
    status: str
    created_at: str
    facts: Optional[CaseFactsData] = None
