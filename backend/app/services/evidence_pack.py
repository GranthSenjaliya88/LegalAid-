"""
Phase 8 — Build My Evidence Pack Service.
Generates an interactive evidence checklist tailored to the user's domain and legal requirements.
Supports checklist items with importance levels (essential vs helpful) and rationale.
"""

from typing import Dict, Any, List
from pydantic import BaseModel


class EvidenceItem(BaseModel):
    item_id: str
    document_name: str
    importance: str  # essential, helpful
    why_it_matters: str
    is_collected: bool = False


class EvidencePackResponse(BaseModel):
    domain: str
    total_items: int
    essential_count: int
    checklist: List[EvidenceItem]


DOMAIN_EVIDENCE_TEMPLATES = {
    "consumer": [
        ("ev_1", "Invoice / Cash Memo / Purchase Bill", "essential", "Establishes proof of purchase and seller identity."),
        ("ev_2", "Payment Receipt / Bank Transfer Statement", "essential", "Confirms financial consideration paid."),
        ("ev_3", "Warranty Card / Service Terms", "essential", "Defines defect remedies and warranty period."),
        ("ev_4", "Product Photos / Videos showing defect", "helpful", "Provides visual proof of defect or non-functionality."),
        ("ev_5", "Written Communications (WhatsApp / Emails)", "essential", "Demonstrates notice sent to seller/manufacturer.")
    ],
    "labor": [
        ("ev_1", "Appointment Letter / Employment Contract", "essential", "Proves employment relationship and agreed salary."),
        ("ev_2", "Bank Account Statement showing salary credits", "essential", "Demonstrates wage payment history and unpaid months."),
        ("ev_3", "Salary Slips / Form 16 / Provident Fund Statement", "helpful", "Establishes monthly remuneration and employee ID."),
        ("ev_4", "Termination Notice / Layoff Email", "essential", "Confirms date and reason for termination."),
        ("ev_5", "Written Demand Notice sent to employer", "helpful", "Proves formal demand for unpaid dues prior to legal action.")
    ],
    "tenant": [
        ("ev_1", "Rent Agreement / Lease Deed", "essential", "Proves tenancy terms, deposit amount, and notice clause."),
        ("ev_2", "Security Deposit Transfer Receipt / Bank Passbook", "essential", "Confirms initial deposit paid to landlord."),
        ("ev_3", "Recent Rent Receipts / Bank Transfer Proof", "helpful", "Demonstrates tenant was up to date on rent payments."),
        ("ev_4", "Notice of Vacating / Deposit Refund Demand Email", "essential", "Proves premises handed over and refund requested."),
        ("ev_5", "Photos / Videos of Handover State of Premises", "helpful", "Counteracts claims of damage by landlord.")
    ],
    "cyber": [
        ("ev_1", "SMS Notification / Email from Bank", "essential", "Shows unauthorized debit timestamp and amount."),
        ("ev_2", "Bank Statement highlighting unauthorized transaction", "essential", "Official record required for bank claim."),
        ("ev_3", "Cyber Crime Portal Acknowledgement Receipt (1930 / cybercrime.gov.in)", "essential", "Mandatory official complaint reference."),
        ("ev_4", "Screenshot of Fraudulent Call Log / Messaging App", "helpful", "Supports investigation into fraud source.")
    ],
    "general": [
        ("ev_1", "Written Agreement / Contract Copy", "essential", "Establishes terms between disputing parties."),
        ("ev_2", "Bank Passbook / Transaction Receipts", "essential", "Proves financial transactions."),
        ("ev_3", "Written Communications (Email / SMS / Letters)", "essential", "Demonstrates dispute history and notice.")
    ]
}


def generate_evidence_pack_service(domain: str) -> EvidencePackResponse:
    """Generate Evidence Pack checklist for given domain."""
    dom_key = domain if domain in DOMAIN_EVIDENCE_TEMPLATES else "general"
    template = DOMAIN_EVIDENCE_TEMPLATES[dom_key]

    items = []
    essential_cnt = 0

    for item_id, name, imp, why in template:
        if imp == "essential":
            essential_cnt += 1
        items.append(EvidenceItem(
            item_id=item_id,
            document_name=name,
            importance=imp,
            why_it_matters=why
        ))

    return EvidencePackResponse(
        domain=dom_key,
        total_items=len(items),
        essential_count=essential_cnt,
        checklist=items
    )
