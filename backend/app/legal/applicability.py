"""
Legal Applicability Engine.
Evaluates whether a legal provision applies based on temporal, jurisdictional, and context constraints.
"""

from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.schemas.legal import RetrievalMatch


def date_applies(
    incident_date: date | None,
    effective_from: date | None,
    effective_to: date | None,
) -> bool:

    if incident_date is None:
        return True

    if effective_from and incident_date < effective_from:
        return False

    if effective_to and incident_date > effective_to:
        return False

    return True


def jurisdiction_applies(
    requested_state: str | None,
    requested_city: str | None,
    section_state: str | None,
    section_city: str | None,
) -> bool:

    if section_state is None:
        return True

    if requested_state is None:
        return False

    if section_state.lower() != requested_state.lower():
        return False

    if section_city:
        if not requested_city:
            return False

        return section_city.lower() == requested_city.lower()

    return True


@dataclass
class ApplicabilityResult:
    status: str
    reasons: list[str]

    def __getitem__(self, item):
        return getattr(self, item)


def check_section_applicability(
    section=None,
    state: str | None = None,
    city: str | None = None,
    incident_date: date | None = None,
    match=None,
    user_state: str | None = None,
    **kwargs
) -> ApplicabilityResult:
    target_section = section if section is not None else match
    target_state = state if state is not None else user_state

    reasons = []

    if not date_applies(
        incident_date,
        getattr(target_section, "effective_from", None),
        getattr(target_section, "effective_to", None),
    ):
        return ApplicabilityResult(
            status="NOT_APPLICABLE",
            reasons=["Incident date is outside the provision's effective range."],
        )

    sec_status = getattr(target_section, "status", "CURRENT")
    status_val = getattr(sec_status, "value", sec_status) if sec_status else "CURRENT"

    if status_val not in {"CURRENT", "HISTORICAL"}:
        return ApplicabilityResult(
            status="INSUFFICIENT_INFORMATION",
            reasons=["Legal status could not be verified."],
        )

    if not jurisdiction_applies(
        target_state,
        city,
        getattr(target_section, "state", None),
        getattr(target_section, "city", None),
    ):
        return ApplicabilityResult(
            status="NOT_APPLICABLE",
            reasons=["Jurisdiction does not match."],
        )

    if status_val == "HISTORICAL":
        reasons.append("Historical provision.")

    if getattr(target_section, "state", None):
        reasons.append(f"State-specific law: {target_section.state}")

    if getattr(target_section, "city", None):
        reasons.append(f"City-specific law: {target_section.city}")

    return ApplicabilityResult(
        status="MAY_APPLY",
        reasons=reasons,
    )


class ApplicabilityEvaluation(BaseModel):
    section_id: Optional[int] = None
    act_name: str
    section_number: str
    applicability_status: str
    matching_factors: List[str]
    missing_factors: List[str]
    disqualifying_factors: List[str]
    applicability_reason: str


def evaluate_provision_applicability(
    match: RetrievalMatch,
    facts: Dict[str, Any]
) -> ApplicabilityEvaluation:
    matching_factors = []
    missing_factors = []
    disqualifying_factors = []

    user_domain = (facts.get("domain") or "").lower()
    user_state = facts.get("state")
    user_date = facts.get("date") or facts.get("incident_date")

    sec_act = (match.act or "").lower()
    sec_state = match.state or "All"
    sec_domain = (match.domain or "").lower()

    if sec_domain and user_domain and sec_domain == user_domain:
        matching_factors.append(f"Domain match: {user_domain.replace('_', ' ').title()}")
    elif sec_domain and user_domain:
        matching_factors.append(f"Related legal domain: {sec_domain}")

    if user_state and user_state != "All":
        if sec_state.lower() == user_state.lower() or sec_state == "All":
            matching_factors.append(f"Jurisdiction match: {user_state}")
        else:
            disqualifying_factors.append(f"State law mismatch: Provision is specific to {sec_state}, but user is in {user_state}")
    else:
        if sec_state != "All":
            missing_factors.append(f"User state location is required (Provision applies to {sec_state})")

    status = (match.status or "CURRENT").upper()
    if status in {"CURRENT", "ACTIVE"}:
        matching_factors.append("Provision is currently active in force")
    elif status in {"HISTORICAL", "REPEALED"}:
        disqualifying_factors.append("Provision has been repealed or subsumed into newer legislation")

    if user_date and ("bns" in sec_act or "nyaya" in sec_act or "2023" in sec_act):
        try:
            from datetime import datetime
            d_val = datetime.strptime(str(user_date), "%Y-%m-%d").date() if isinstance(user_date, str) else user_date
            if d_val < date(2024, 7, 1):
                disqualifying_factors.append("Offense date (2022) precedes July 1, 2024 (BNS enforcement date); governed by historical IPC 1860")
        except Exception:
            pass

    if disqualifying_factors:
        status_eval = "NOT_APPLICABLE"
        reason = f"Not applicable: {'; '.join(disqualifying_factors)}."
    elif missing_factors and len(matching_factors) < 2:
        status_eval = "INSUFFICIENT_INFORMATION"
        reason = f"Insufficient details: {'; '.join(missing_factors)}."
    elif missing_factors:
        status_eval = "CONDITIONALLY_APPLICABLE"
        reason = f"Conditionally applicable based on available facts. Note: {'; '.join(missing_factors)}."
    else:
        status_eval = "APPLICABLE"
        reason = f"Fully applicable: {'; '.join(matching_factors)}."

    return ApplicabilityEvaluation(
        section_id=None,
        act_name=match.act,
        section_number=match.section,
        applicability_status=status_eval,
        matching_factors=matching_factors,
        missing_factors=missing_factors,
        disqualifying_factors=disqualifying_factors,
        applicability_reason=reason,
    )
