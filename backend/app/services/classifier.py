"""
Case Classifier Service (Phase 5).
Categorizes input domain into consumer, labor, tenant, general_civic.
Invokes AIClient while prohibiting the classifier from deciding or outputting legal section numbers.
"""

from typing import Dict, Any
from app.ai.client import ai_client
from app.schemas.case import CaseFactsData
from app.schemas.analysis import ClassifyResponseData


def classify_case_service(text: str) -> ClassifyResponseData:
    """Classify domain and extract structured facts from user text."""
    ai_result = ai_client.classify_case(text)

    ALLOWED_CLASSIFIER_DOMAINS = {
        "consumer", "labor", "tenant", "cyber", "criminal", "civil", "contract", "family",
        "women_rights", "children_rights", "banking", "traffic", "property", "employment_benefits",
        "constitutional", "procedural", "evidence", "sc_st_protection", "disability_rights",
        "senior_citizens", "education", "digital_online", "healthcare", "human_rights",
        "public_services", "livelihood", "environment", "insolvency", "general"
    }

    domain = str(ai_result.get("domain", "general")).lower()
    if domain in ("rental", "tenant"):
        domain = "tenant"
    elif domain in ("employment", "labor", "labour"):
        domain = "labor"
    elif domain in ("financial_fraud", "banking_fraud"):
        domain = "cyber"
    elif domain not in ALLOWED_CLASSIFIER_DOMAINS:
        domain = "general"

    subdomain = ai_result.get("subdomain")
    confidence = float(ai_result.get("confidence", 0.95))
    jurisdiction_required = bool(ai_result.get("jurisdiction_required", domain == "tenant"))
    urgency = str(ai_result.get("urgency", "low")).lower()

    raw_facts = ai_result.get("facts", {})

    facts = CaseFactsData(
        parties=raw_facts.get("parties"),
        incident=raw_facts.get("incident") or text[:200],
        date=raw_facts.get("date"),
        location=raw_facts.get("location"),
        state=raw_facts.get("state") or raw_facts.get("location"),
        subdomain=subdomain or raw_facts.get("subdomain"),
        amount=raw_facts.get("amount"),
        agreement_exists=raw_facts.get("agreement_exists"),
        notice_given=raw_facts.get("notice_given"),
        desired_outcome=raw_facts.get("desired_outcome"),
        urgency=urgency or raw_facts.get("urgency", "low"),
        additional_facts=raw_facts.get("additional_facts")
    )

    return ClassifyResponseData(
        domain=domain,
        subdomain=subdomain,
        confidence=confidence,
        jurisdiction_required=jurisdiction_required,
        urgency=urgency,
        facts=facts
    )
