"""Pydantic schemas for Case intake and session status."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class CreateCaseRequest(BaseModel):
    text: Optional[str] = Field(None, description="User's legal problem description (Hindi or English)")
    prompt: Optional[str] = Field(None, description="Alias for text field")
    language: str = Field(default="en", description="Language code: 'en' or 'hi'")
    session_id: Optional[str] = Field(None, description="Optional session tracking identifier")

    def __init__(self, **data: Any):
        if "text" not in data and "prompt" in data:
            data["text"] = data["prompt"]
        if "text" not in data or not data["text"]:
            data["text"] = data.get("prompt", "Default intake description")
        super().__init__(**data)


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
