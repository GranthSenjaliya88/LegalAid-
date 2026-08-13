"""
Action Roadmap Service (Requirements #20, #21, #22).
Generates step-by-step action roadmaps and urgency alerts for user guidance.
"""

from typing import Dict, Any, List
from app.schemas.analysis import ActionStepItem, ActionRoadmapResponseData


def generate_action_roadmap(
    domain: str,
    subdomain: str | None,
    urgency: str,
    facts: Dict[str, Any]
) -> ActionRoadmapResponseData:
    """Generate sequential action steps and urgency warning banner."""
    steps: List[ActionStepItem] = []
    urgent_warning: str | None = None

    domain_lower = (domain or "").lower()

    if urgency == "urgent" or domain_lower == "cyber":
        urgent_warning = (
            "🔴 URGENT SITUATION DETECTED: Immediate action is required. "
            "Financial fraud or emergency safety rights must be acted upon without delay."
        )

        steps.append(ActionStepItem(
            step_number=1,
            title="Immediately Freeze Account / Report to Bank & Cyber Cell",
            description="Call 1930 (National Cyber Crime Helpline) or file online at cybercrime.gov.in. Notify your bank in writing immediately to lock card/account and invoke RBI 72-hour Zero Liability protection.",
            required_document="Bank Statement & Transaction SMS Screenshots",
            next_action="Obtain written bank acknowledgement and Cyber Complaint Reference ID."
        ))
        steps.append(ActionStepItem(
            step_number=2,
            title="Preserve Digital Evidence",
            description="Export account statements, save SMS alerts, email confirmations, and call records without deleting any messages.",
            required_document="Transaction Records & Call Logs",
            next_action="Compile digital evidence package into PDF or printed copies."
        ))
        steps.append(ActionStepItem(
            step_number=3,
            title="Draft & Submit Formal Cyber Complaint",
            description="Use LegalAId to generate a formal Cyber Complaint document detailing unauthorized transfer particulars.",
            required_document="LegalAId Generated Cyber Complaint",
            next_action="Submit complaint copy to your local police cyber cell and bank nodal officer."
        ))
        steps.append(ActionStepItem(
            step_number=4,
            title="Escalate to Banking Ombudsman if Unresolved",
            description="If the bank fails to resolve your unauthorized transaction within 30 days, file an online complaint with the RBI Ombudsman (cms.rbi.org.in).",
            required_document="Bank Intimation Letter & Complaint Acknowledgement",
            next_action="Track RBI Ombudsman complaint status online."
        ))

    elif domain_lower == "tenant":
        steps.append(ActionStepItem(
            step_number=1,
            title="Collect Tenancy Proof & Deposit Receipts",
            description="Gather your written tenancy agreement, security deposit payment receipts, rent slips, and notice of vacating.",
            required_document="Rent Agreement & Payment Receipts",
            next_action="Verify exact deposit amount and vacating date."
        ))
        steps.append(ActionStepItem(
            step_number=2,
            title="Send Formal Written Communication",
            description="Send a formal demand message/email to the landlord citing agreed terms and requesting deposit return within 7 to 15 days.",
            required_document="Written Demand Notice / WhatsApp / Email",
            next_action="Wait for 15-day notice period response."
        ))
        steps.append(ActionStepItem(
            step_number=3,
            title="Draft Legal Notice",
            description="Generate a formal Tenant Legal Notice using LegalAId citing Model Tenancy Act / State Rent Control Act provisions.",
            required_document="LegalAId Generated Tenant Notice",
            next_action="Send notice via Registered Post AD or email."
        ))
        steps.append(ActionStepItem(
            step_number=4,
            title="Approach Rent Authority / Rent Court",
            description="If deposit is unreturned or essential services cut off, file a petition before the local Rent Authority / Rent Controller.",
            required_document="Tenant Legal Notice & Postal Proof",
            next_action="Consult a qualified advocate for representation before Rent Court."
        ))

    elif domain_lower == "labor":
        steps.append(ActionStepItem(
            step_number=1,
            title="Gather Employment & Wage Records",
            description="Compile appointment letter, salary slips, bank statements showing wage non-payment, and attendance logs.",
            required_document="Appointment Letter & Salary Slips",
            next_action="Calculate total unpaid wages, notice pay, or gratuity due."
        ))
        steps.append(ActionStepItem(
            step_number=2,
            title="Send Internal Salary Demand Letter",
            description="Submit a written demand to HR / employer specifying unpaid months and requesting settlement within 15 days.",
            required_document="Salary Demand Email / Letter",
            next_action="Track employer response during notice window."
        ))
        steps.append(ActionStepItem(
            step_number=3,
            title="Generate Formal Labor Notice",
            description="Draft a formal Legal Demand Notice under Industrial Disputes Act 1947 or Payment of Wages Act.",
            required_document="LegalAId Salary Demand Notice",
            next_action="Send notice via Registered Post AD."
        ))
        steps.append(ActionStepItem(
            step_number=4,
            title="File Grievance with Labor Commissioner / Conciliation Officer",
            description="Approach the Assistant Labor Commissioner (ALC) office in your district to initiate conciliation proceedings.",
            required_document="Labor Complaint & Registered Post AD Receipt",
            next_action="Attend conciliation hearing before Labor Officer."
        ))

    elif domain_lower == "consumer":
        steps.append(ActionStepItem(
            step_number=1,
            title="Preserve Product Invoice & Defect Proof",
            description="Keep the original tax invoice, warranty card, customer service emails, and clear photos/videos of the defect.",
            required_document="Invoice & Service Inspection Report",
            next_action="Document seller/brand refusal response."
        ))
        steps.append(ActionStepItem(
            step_number=2,
            title="Register Complaint on National Consumer Helpline (NCH)",
            description="Call 1915 or register online at consumerhelpline.gov.in for informal pre-litigation resolution.",
            required_document="NCH Docket ID",
            next_action="Monitor 15-day NCH resolution portal status."
        ))
        steps.append(ActionStepItem(
            step_number=3,
            title="Draft & Serve Legal Notice to Seller/Manufacturer",
            description="Generate a formal Consumer Dispute Notice under Consumer Protection Act 2019 using LegalAId.",
            required_document="LegalAId Consumer Notice",
            next_action="Dispatch notice via Registered Post or official company email."
        ))
        steps.append(ActionStepItem(
            step_number=4,
            title="File e-Daakhil Complaint at District Consumer Commission",
            description="If unaddressed, file a consumer complaint online at edaakhil.nic.in before the District Consumer Disputes Redressal Commission.",
            required_document="e-Daakhil Petition, Invoice & Legal Notice Copy",
            next_action="Track consumer commission court hearing date."
        ))

    else:
        steps.append(ActionStepItem(
            step_number=1,
            title="Collect Supporting Documents",
            description="Organize bills, agreements, bank statements, and written communications related to the dispute.",
            required_document="Primary Contract / Proof",
            next_action="Establish timeline of events."
        ))
        steps.append(ActionStepItem(
            step_number=2,
            title="Draft & Serve Formal Legal Notice",
            description="Use LegalAId to draft a formal legal notice stating the facts and legal grounds for your demand.",
            required_document="LegalAId Generated Legal Notice",
            next_action="Send notice to counterparty with a 15-day deadline."
        ))
        steps.append(ActionStepItem(
            step_number=3,
            title="Consult Qualified Legal Professional",
            description="If counterparty fails to comply within notice period, consult a licensed advocate to evaluate court proceedings.",
            required_document="Legal Notice Copy & Postal Proof",
            next_action="Schedule consultation with advocate."
        ))

    return ActionRoadmapResponseData(
        urgency=urgency,
        urgent_warning=urgent_warning,
        steps=steps
    )
