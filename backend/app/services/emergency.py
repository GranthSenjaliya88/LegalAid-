"""
Phase 7 — Emergency Action Mode Service.
Detects high-risk legal emergency situations (cyber fraud, unauthorized bank transfers, domestic violence, illegal eviction, physical threats).
Renders verified, immediate actionable steps with official government emergency helplines.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class EmergencyActionPlan(BaseModel):
    is_urgent: bool
    emergency_type: str
    headline: str
    immediate_steps: List[str]
    evidence_to_preserve: List[str]
    official_authority: str
    contact_helpline: str
    online_portal_url: str
    reference_number_note: str


EMERGENCY_PROFILES = {
    "cyber_banking": EmergencyActionPlan(
        is_urgent=True,
        emergency_type="UNAUTHORIZED_BANK_TRANSACTION",
        headline="🚨 URGENT ACTION: Report within 72 Hours for Zero Liability Protection",
        immediate_steps=[
            "1. Immediately block your bank card / net banking access via your bank's emergency customer helpline.",
            "2. File an official complaint on the National Cyber Crime Reporting Portal (cybercrime.gov.in) or call 1930.",
            "3. Submit a written complaint to your bank branch within 72 hours under RBI Zero Liability Directives."
        ],
        evidence_to_preserve=[
            "SMS alert / email notification received from bank",
            "Bank account statement highlighting transaction",
            "Cyber Crime Portal complaint acknowledgment copy"
        ],
        official_authority="National Cyber Crime Reporting Portal & RBI Ombudsman",
        contact_helpline="1930 (National Cyber Fraud Helpline) / 14448 (RBI Ombudsman)",
        online_portal_url="https://cybercrime.gov.in",
        reference_number_note="Save the 15-digit Cyber Crime Complaint Acknowledgement Number for your bank claim."
    ),
    "women_safety": EmergencyActionPlan(
        is_urgent=True,
        emergency_type="DOMESTIC_VIOLENCE_HARASSMENT",
        headline="🚨 URGENT ACTION: Immediate Protection & National Commission Help",
        immediate_steps=[
            "1. Call 112 (National Emergency Helpline) or 1091 (Women Helpline) if you are in immediate danger.",
            "2. Contact the National Commission for Women (NCW) 24/7 Helpline or file an online complaint at ncw.nic.in.",
            "3. Reach out to the local Protection Officer appointed under the Domestic Violence Act 2005."
        ],
        evidence_to_preserve=[
            "Medical records / injury reports (if physical harm occurred)",
            "Threatening messages, emails, audio/video recordings",
            "Police complaint copy / General Diary entry"
        ],
        official_authority="National Commission for Women & Protection Officer",
        contact_helpline="112 (Emergency) / 7827170170 (NCW 24/7 Helpline)",
        online_portal_url="https://ncw.nic.in",
        reference_number_note="Store your NCW Complaint Reference Number securely."
    ),
    "illegal_eviction": EmergencyActionPlan(
        is_urgent=True,
        emergency_type="ILLEGAL_EVICTION_LOCKOUT",
        headline="🚨 URGENT ACTION: Unlawful Eviction Protection",
        immediate_steps=[
            "1. Do not vacate premises under force. Landlords cannot evict without a court decree or Rent Authority order.",
            "2. File an immediate complaint at the local police station regarding unlawful lockout or intimidation.",
            "3. Submit an urgent petition before the Rent Controller / Rent Tribunal for restoration of possession."
        ],
        evidence_to_preserve=[
            "Rent Agreement / Lease Copy",
            "Recent Rent Payment Receipts / UPI Bank Transfer proof",
            "Photos / videos of locks changed or utility disconnection"
        ],
        official_authority="Rent Authority / Civil Court & Local Police Station",
        contact_helpline="112 (Police Emergency)",
        online_portal_url="https://mohua.gov.in",
        reference_number_note="Obtain a signed Police Acknowledgement Receipt for your complaint."
    )
}


def detect_and_generate_emergency_plan(facts: Dict[str, Any], domain: str) -> Optional[EmergencyActionPlan]:
    """Detect if incident requires Urgent Action Mode and return verified plan."""
    incident = (facts.get("incident") or "").lower()
    dom = (domain or "").lower()

    if dom == "cyber" or "unauthorized" in incident or "bank" in incident or "otp" in incident or "fraud" in incident:
        return EMERGENCY_PROFILES["cyber_banking"]
    elif dom == "women_rights" or "domestic violence" in incident or "harassment" in incident or "stalking" in incident:
        return EMERGENCY_PROFILES["women_safety"]
    elif dom == "tenant" and ("evict" in incident or "lockout" in incident or "thrown out" in incident):
        return EMERGENCY_PROFILES["illegal_eviction"]

    return None
