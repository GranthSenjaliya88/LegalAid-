"""
LegalAId — Cases router  (Step 2)

Endpoints
---------
POST  /case                   — Create a new case session; returns case_id.
POST  /case/{case_id}/message — Run the classifier on the user's message.
GET   /case/{case_id}         — Retrieve current case state.

State is held in an in-process dict for now.  Step 3 (Retrieval) will read
the classified_domain and extracted_facts from here to drive corpus search.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException

from app.agents.classifier import classify
from app.schemas import (
    CaseMessage,
    CaseState,
    ClassifierOutput,
    CreateCaseResponse,
    ExtractedFacts,
    UpdateFactsRequest,
)

router = APIRouter(prefix="/case", tags=["case"])

# ──────────────────────────────────────────────────────────────────────────────
# In-memory store  (replaced by DB in a later step)
# ──────────────────────────────────────────────────────────────────────────────

_cases: dict[str, dict[str, Any]] = {}


def _new_case() -> dict[str, Any]:
    return {
        "case_id": str(uuid.uuid4()),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "messages": [],          # list of {role, text, ts}
        "classifier_output": None,   # ClassifierOutput dict, set after first message
        "step": "awaiting_input",
    }


# ──────────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────────

@router.post("", response_model=CreateCaseResponse, status_code=201,
             summary="Start a new case session")
def create_case():
    """
    Create a blank case and return its ID.  The frontend calls this once,
    then posts all messages to /case/{id}/message.
    """
    case = _new_case()
    _cases[case["case_id"]] = case
    return CreateCaseResponse(case_id=case["case_id"])


@router.post("/{case_id}/message", response_model=CaseState,
             summary="Send a message — runs the Classifier Agent")
def post_message(case_id: str, body: CaseMessage):
    """
    Run the Classifier Agent on the user's free-form text.

    The classifier:
    - Determines the legal domain (consumer | labor | tenant | other)
    - Extracts structured facts (parties, dates, amounts, issue_summary, user_goal)

    It does NOT cite any law or give any legal opinion — that is Step 3.
    Returns the full case state including the classifier output.
    """
    case = _cases.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found. Create one via POST /case first.")

    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Message text must not be empty.")

    # Append user turn
    case["messages"].append({
        "role": "user",
        "text": text,
        "ts": datetime.utcnow().isoformat() + "Z",
    })

    # ── Run classifier ──────────────────────────────────────────────────────
    try:
        result: ClassifierOutput = classify(text)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Classifier unavailable: {exc}") from exc

    case["classifier_output"] = result.model_dump()
    case["step"] = "classified"

    # Append a synthetic assistant turn so the frontend sees it in history
    case["messages"].append({
        "role": "assistant",
        "text": f"[classified:{result.classified_domain}]",
        "ts": datetime.utcnow().isoformat() + "Z",
    })

    return _to_case_state(case)


@router.patch("/{case_id}/facts", response_model=CaseState,
              summary="Update or confirm extracted facts for a case")
def update_case_facts(case_id: str, body: UpdateFactsRequest):
    """
    Update the classified domain and/or extracted facts for a case after user correction in the frontend.
    """
    case = _cases.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    if not case.get("classifier_output"):
        raise HTTPException(status_code=400, detail="Case has not been classified yet.")

    current_output = ClassifierOutput(**case["classifier_output"])
    current_facts = current_output.extracted_facts.model_dump()

    if body.extracted_facts:
        new_facts_dict = body.extracted_facts.model_dump(exclude_unset=True)
        current_facts.update(new_facts_dict)

    new_domain = body.classified_domain or current_output.classified_domain

    updated_output = ClassifierOutput(
        classified_domain=new_domain,
        extracted_facts=ExtractedFacts(**current_facts),
    )
    case["classifier_output"] = updated_output.model_dump()
    return _to_case_state(case)


@router.get("/{case_id}", response_model=CaseState,
            summary="Get the current state of a case")
def get_case(case_id: str):
    """Retrieve the current classifier output and message history for a case."""
    case = _cases.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
    return _to_case_state(case)


# ──────────────────────────────────────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────────────────────────────────────

def _to_case_state(case: dict[str, Any]) -> CaseState:
    classifier_output = None
    if case.get("classifier_output"):
        classifier_output = ClassifierOutput(**case["classifier_output"])
    return CaseState(
        case_id=case["case_id"],
        created_at=case["created_at"],
        step=case["step"],
        messages=case["messages"],
        classifier_output=classifier_output,
    )
