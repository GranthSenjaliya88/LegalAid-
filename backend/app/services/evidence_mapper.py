"""
Evidence Mapper Service (Requirement #19).
Converts legal claims and domains into tailored evidence suggestions.
"""

from typing import Dict, Any, List
from app.schemas.analysis import EvidenceItem, EvidenceResponseData


def generate_evidence_checklist(
    domain: str,
    subdomain: str | None,
    facts: Dict[str, Any]
) -> EvidenceResponseData:
    """Generate evidence checklist mapped to the user's specific domain and facts."""
    checklist: List[EvidenceItem] = []
    incident = facts.get("incident") or "Legal claim"

    domain_lower = (domain or "").lower()
    subdomain_lower = (subdomain or "").lower()

    if domain_lower == "labor":
        checklist.append(EvidenceItem(
            document_name="Employment Contract / Appointment Letter",
            importance="essential",
            why_it_matters="Proves employer-employee relationship, designation, salary terms, and notice period obligations."
        ))
        checklist.append(EvidenceItem(
            document_name="Salary Slips / Bank Statements",
            importance="essential",
            why_it_matters="Establishes history of salary payments and exact period of unpaid wages/defaults."
        ))
        checklist.append(EvidenceItem(
            document_name="Written Demand / Termination Letter / Emails",
            importance="supporting",
            why_it_matters="Demonstrates formal communication, demand for unpaid dues, or termination date."
        ))
        checklist.append(EvidenceItem(
            document_name="Attendance Records / ID Card / Work Communications",
            importance="supporting",
            why_it_matters="Confirms active service days during the disputed payment period."
        ))

    elif domain_lower == "tenant":
        checklist.append(EvidenceItem(
            document_name="Rent Agreement / Lease Deed",
            importance="essential",
            why_it_matters="Proves tenancy terms, agreed monthly rent, and stipulated security deposit refund rules."
        ))
        checklist.append(EvidenceItem(
            document_name="Security Deposit Payment Receipt / UPI Transaction ID",
            importance="essential",
            why_it_matters="Definitively proves the exact deposit amount handed over to the landlord."
        ))
        checklist.append(EvidenceItem(
            document_name="Vacating Notice & Key Handover Receipts / Messages",
            importance="supporting",
            why_it_matters="Confirms the exact date premises were vacated in accordance with notice terms."
        ))
        checklist.append(EvidenceItem(
            document_name="Property Condition Photos / Inspection Notes",
            importance="supporting",
            why_it_matters="Counters false landlord claims of property damage used to withhold deposit."
        ))

    elif domain_lower == "consumer":
        checklist.append(EvidenceItem(
            document_name="Tax Invoice / Cash Memo / Purchase Receipt",
            importance="essential",
            why_it_matters="Establishes consumer status, purchase date, price paid, and seller identity."
        ))
        checklist.append(EvidenceItem(
            document_name="Warranty Card / Guarantee Certificate",
            importance="essential",
            why_it_matters="Proves coverage terms and manufacturer/seller obligation to repair or replace."
        ))
        checklist.append(EvidenceItem(
            document_name="Photos / Videos / Service Center Inspection Report",
            importance="supporting",
            why_it_matters="Demonstrates the defect or failure of the product/service in question."
        ))
        checklist.append(EvidenceItem(
            document_name="Customer Care Emails / Complaint Reference Numbers",
            importance="supporting",
            why_it_matters="Proves you attempted informal resolution before filing a formal notice/complaint."
        ))

    elif domain_lower == "cyber":
        checklist.append(EvidenceItem(
            document_name="Bank Account Statement showing Fraudulent Debit",
            importance="essential",
            why_it_matters="Definitively shows unauthorized transaction amount, date, time, and recipient account."
        ))
        checklist.append(EvidenceItem(
            document_name="SMS Alerts / Transaction Notification Screenshots",
            importance="essential",
            why_it_matters="Establishes exact timestamp when the unauthorized transfer occurred."
        ))
        checklist.append(EvidenceItem(
            document_name="Written Bank Intimation / Acknowledgement within 72 hrs",
            importance="essential",
            why_it_matters="Mandatory under RBI guidelines to qualify for Zero Liability customer protection."
        ))
        checklist.append(EvidenceItem(
            document_name="National Cybercrime Portal (1930 / cybercrime.gov.in) Complaint ID",
            importance="supporting",
            why_it_matters="Official police acknowledgement for tracking and freezing stolen funds."
        ))

    else:
        checklist.append(EvidenceItem(
            document_name="Primary Agreement / Written Contract / Bill",
            importance="essential",
            why_it_matters="Establishes legal relationship and responsibilities between parties."
        ))
        checklist.append(EvidenceItem(
            document_name="Payment Proof / Receipts / Bank Records",
            importance="essential",
            why_it_matters="Demonstrates financial flow or monetary default."
        ))
        checklist.append(EvidenceItem(
            document_name="Written Communications (Emails, WhatsApp, Letters)",
            importance="supporting",
            why_it_matters="Proves demand, refusal, or notice exchanged prior to legal proceedings."
        ))

    return EvidenceResponseData(
        claim_summary=f"Evidence suggestions for {domain.title()} case ({subdomain or 'general'})",
        checklist=checklist
    )
