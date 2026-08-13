"""
Clarification Engine Service (Phase 7).
Determines missing information needed to establish rights.
Generates max 3 questions and updates case facts upon user response.
"""

from typing import Dict, Any, List
from app.ai.client import ai_client
from app.schemas.analysis import ClarifyResponseData
from app.schemas.case import CaseFactsData


def evaluate_clarification(facts: CaseFactsData, domain: str | None = None) -> ClarifyResponseData:
    """Evaluate whether clarification questions are needed based on missing facts."""
    facts_dict = facts.model_dump() if hasattr(facts, "model_dump") else (facts if isinstance(facts, dict) else {})
    if domain:
        facts_dict["domain"] = domain

    ai_result = ai_client.generate_clarifying_questions(facts_dict)

    needs = bool(ai_result.get("needs_clarification", False))
    questions: List[str] = ai_result.get("questions", [])[:3]
    missing: List[str] = ai_result.get("missing_facts", [])

    # Special state awareness requirement check
    if domain in ("tenant", "labor") and not facts_dict.get("state") and "state" not in missing:
        questions.insert(0, "Which state or Union Territory is the property or workplace located in?")
        missing.insert(0, "state")
        needs = True
        questions = questions[:3]

    return ClarifyResponseData(
        needs_clarification=needs and len(questions) > 0,
        questions=questions,
        missing_facts=missing
    )


def update_facts_from_answers(current_facts: Dict[str, Any], answers: Dict[str, Any]) -> Dict[str, Any]:
    """Merge user clarification answers into case facts."""
    updated = dict(current_facts)

    for key, val in answers.items():
        if val is not None:
            updated[key] = val

    return updated
