"""
Local Legal Reasoning Engine for LegalAId.
All classification, clarification, explanation, and drafting logic runs 100% locally
without any external API calls, cloud dependencies, or network latency.
Includes input sanitization, deterministic statutory mapping, and template-based legal generation.
"""

import re
import json
from typing import Dict, Any, Optional, List
from app.core.logging import logger
from app.core.security import sanitize_for_prompt


class AIClient:
    """Local legal reasoning client operating entirely offline."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = ""
        self.model = "local-engine"

    @property
    def is_available(self) -> bool:
        """Local engine is always available without external API dependencies."""
        return True

    def classify_case(self, text: str) -> Dict[str, Any]:
        """Classify domain and extract initial facts using local deterministic analysis."""
        safe_text = sanitize_for_prompt(text)
        return self._heuristic_classify(safe_text)

    def generate_clarifying_questions(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        """Identify missing facts and generate targeted clarifying questions locally."""
        return self._heuristic_clarify(facts)

    def explain_retrieved_law(
        self,
        retrieved_sections: List[Dict[str, Any]],
        case_facts: Dict[str, Any],
        language: str = "en"
    ) -> Dict[str, Any]:
        """Generate rights explanation strictly grounded on retrieved statutory sections."""
        return self._heuristic_explain(retrieved_sections, case_facts, language)

    def fill_document_template(
        self,
        doc_type: str,
        verified_sections: List[Dict[str, Any]],
        case_facts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fill structured document template fields locally using case facts and verified citations."""
        return self._heuristic_fill_document(doc_type, verified_sections, case_facts)

    # -------------------------------------------------------------------------
    # Local Deterministic Legal Engines
    # -------------------------------------------------------------------------

    def _heuristic_classify(self, text: str) -> Dict[str, Any]:
        lower = text.lower()
        subdomain = "general_dispute"
        urgency = "low"

        def _has_kw(keywords: List[str]) -> bool:
            for kw in keywords:
                if len(kw) <= 3:
                    if re.search(r"\b" + re.escape(kw) + r"\b", lower):
                        return True
                else:
                    if kw in lower:
                        return True
            return False

        if _has_kw(["bank", "transfer", "unauthorized", "phishing", "cyber", "hacked", "stolen money", "account debit", "サイバー", "ओटीपी", "खाता", "otp", "online scam", "1930"]):
            domain = "cyber"
            subdomain = "unauthorized_bank_transfer"
            urgency = "urgent"
        elif _has_kw(["landlord", "tenant", "rent", "deposit", "evict", "मकान", "किराया", "जमानत", "lease", "drca", "mrca", "kra", "mta"]):
            domain = "tenant"
            if any(w in lower for w in ["evict", "water", "electricity", "cut off", "force", "lock"]):
                subdomain = "illegal_eviction"
                urgency = "urgent" if ("cut off" in lower or "force" in lower or "lock" in lower) else "high"
            else:
                subdomain = "security_deposit"
                urgency = "medium"
        elif _has_kw(["salary", "wage", "employer", "employee", "fired", "gratuity", "pf", "maternity", "retrenchment", "severance", "vesan", "ветан", "वेतन", "नौकरी", "fnf", "settlement"]):
            domain = "labor"
            subdomain = "unpaid_wages"
            urgency = "medium"
        elif _has_kw(["refund", "warranty", "defective", "flipkart", "amazon", "product", "mrp", "e-commerce", "defect", "deficiency", "cpa", "रिफंड", "वारंटी", "seller", "replacement"]):
            domain = "consumer"
            subdomain = "product_defect"
            urgency = "medium"
        elif _has_kw(["fir", "zero fir", "police", "bnss", "thana", "investigation", "magistrate complaint"]):
            domain = "procedural"
            subdomain = "police_complaint"
            urgency = "high"
        elif _has_kw(["evidence", "whatsapp chat", "65b", "bsa", "digital proof", "admissible"]):
            domain = "evidence"
            subdomain = "digital_evidence"
            urgency = "low"
        elif _has_kw(["bns", "theft", "stolen", "extortion", "cheating", "fraud", "intimidation", "threat", "dhamki", "chori", "dhokhadhadi", "blackmail", "mischief", "property damage"]):
            domain = "criminal"
            subdomain = "general_crime"
            urgency = "high"
        elif _has_kw(["cheque", "bounce", "138", "ni act", "rbi", "ombudsman"]):
            domain = "banking"
            subdomain = "cheque_bounce"
            urgency = "high"
        elif _has_kw(["posh", "sexual harassment", "domestic violence", "husband", "in laws", "abuse", "woman", "women", "ncw"]):
            domain = "women_rights"
            subdomain = "women_safety"
            urgency = "high"
        elif _has_kw(["senior citizen", "parent", "maintenance tribunal", "elder"]):
            domain = "senior_citizens"
            subdomain = "maintenance_rights"
            urgency = "medium"
        elif _has_kw(["sc", "st", "caste", "atrocities", "slur"]):
            domain = "sc_st_protection"
            subdomain = "atrocities_prevention"
            urgency = "high"
        elif _has_kw(["disability", "disabled", "rpwd", "handicap"]):
            domain = "disability_rights"
            subdomain = "non_discrimination"
            urgency = "medium"
        elif _has_kw(["contract", "agreement", "breach", "damages"]):
            domain = "contract"
            subdomain = "breach_of_contract"
            urgency = "medium"
        elif _has_kw(["lessor", "lessee", "property defect", "tpa"]):
            domain = "property"
            subdomain = "lease_rights"
            urgency = "medium"
        elif _has_kw(["dpdp", "data privacy", "privacy leak"]):
            domain = "digital_online"
            subdomain = "data_privacy"
            urgency = "medium"
        elif _has_kw(["good samaritan", "traffic", "road accident"]):
            domain = "traffic"
            subdomain = "accident_help"
            urgency = "low"
        elif _has_kw(["article 21", "fundamental right", "liberty"]):
            domain = "constitutional"
            subdomain = "fundamental_rights"
            urgency = "medium"
        else:
            domain = "general"
            subdomain = "general_claim"

        # Detect Indian states/UTs
        states_map = {
            "delhi": "Delhi", "mumbai": "Maharashtra", "maharashtra": "Maharashtra",
            "bengaluru": "Karnataka", "bangalore": "Karnataka", "karnataka": "Karnataka",
            "chennai": "Tamil Nadu", "tamil nadu": "Tamil Nadu", "up": "Uttar Pradesh",
            "uttar pradesh": "Uttar Pradesh", "haryana": "Haryana", "gurgaon": "Haryana",
            "gurugram": "Haryana", "noida": "Uttar Pradesh", "punjab": "Punjab",
            "gujarat": "Gujarat", "kolkata": "West Bengal", "bengal": "West Bengal"
        }
        detected_state = None
        for k, v in states_map.items():
            if re.search(r"\b" + re.escape(k) + r"\b", lower):
                detected_state = v
                break

        amounts = re.findall(r"(?:₹|rs\.?|rupees?|रुपये?)\s?[\d,]+|[\d,]+\s?(?:rs\.?|rupees?|रुपये?)", text, re.IGNORECASE)
        dates = re.findall(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\b(?:last|this)\s+(?:month|year|week)\b", text, re.IGNORECASE)

        return {
            "domain": domain,
            "subdomain": subdomain,
            "confidence": 0.95,
            "jurisdiction_required": domain == "tenant",
            "urgency": urgency,
            "facts": {
                "parties": "Aggrieved User vs Opposite Party",
                "incident": text[:200],
                "date": ", ".join(dates) if dates else None,
                "location": detected_state,
                "state": detected_state,
                "subdomain": subdomain,
                "amount": ", ".join(amounts) if amounts else None,
                "agreement_exists": None,
                "notice_given": None,
                "desired_outcome": "Immediate resolution and legal remedy",
                "urgency": urgency
            }
        }

    def _heuristic_clarify(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        domain = facts.get("domain") or facts.get("subdomain") or ""
        incident_text = str(facts.get("incident") or "")
        
        # Cyber / Banking / Consumer disputes with detailed incident text do not need agreement clarification
        if domain in ("cyber", "unauthorized_bank_transfer", "consumer", "digital_online") or len(incident_text) > 80:
            return {
                "needs_clarification": False,
                "questions": [],
                "missing_facts": []
            }

        questions = []
        missing = []
        
        if not facts.get("amount") and "amount" not in incident_text.lower():
            questions.append("What is the exact financial amount or transaction value involved?")
            missing.append("amount")
            
        if domain in ("tenant", "labor") and facts.get("agreement_exists") is None:
            questions.append("Was there a written rental agreement or employment contract?")
            missing.append("agreement_exists")

        return {
            "needs_clarification": len(questions) > 0,
            "questions": questions[:3],
            "missing_facts": missing[:3]
        }

    def _heuristic_explain(
        self,
        retrieved_sections: List[Dict[str, Any]],
        case_facts: Dict[str, Any],
        language: str = "en"
    ) -> Dict[str, Any]:
        if not retrieved_sections:
            return {
                "summary": "No matching statutory sections were found in the database for your issue.",
                "rights": [],
                "next_steps": ["Consult a licensed advocate to evaluate your remedies."],
                "confidence": "low"
            }

        rights_items = []
        for sec in retrieved_sections:
            act_name = sec.get("act") or sec.get("act_short_name") or "Statute"
            sec_num = sec.get("section") or sec.get("section_number") or ""
            title = sec.get("title") or "General Protection"
            text = sec.get("relevant_text") or sec.get("text") or ""
            ref = sec.get("source_reference") or f"Section {sec_num} of {act_name}"

            rights_items.append({
                "explanation": f"Under Section {sec_num} ({title}), {text[:180]}...",
                "citations": [{
                    "act": act_name,
                    "section": sec_num,
                    "source_reference": ref
                }]
            })

        summary = f"Based on the database corpus, {len(retrieved_sections)} relevant statutory sections apply to your issue."
        if language == "hi":
            summary = f"डेटाबेस कॉर्पस के आधार पर, आपके मामले में {len(retrieved_sections)} संबंधित कानूनी धाराएं लागू होती हैं।"

        return {
            "summary": summary,
            "rights": rights_items,
            "next_steps": [
                "Gather all relevant receipts, agreements, and correspondence.",
                "Send a formal legal notice referencing the cited statute sections.",
                "File a complaint with the designated tribunal or authority if unaddressed."
            ],
            "confidence": "high"
        }

    def _heuristic_fill_document(
        self,
        doc_type: str,
        verified_sections: List[Dict[str, Any]],
        case_facts: Dict[str, Any]
    ) -> Dict[str, Any]:
        parties = case_facts.get("parties") or "Aggrieved Party vs Opposite Party"
        incident = case_facts.get("incident") or "Legal dispute"
        amount = case_facts.get("amount") or "unspecified amount"
        outcome = case_facts.get("desired_outcome") or "immediate resolution"

        sec_citations = []
        for s in verified_sections:
            act = s.get("act") or s.get("act_short_name") or ""
            num = s.get("section") or s.get("section_number") or ""
            if act and num:
                sec_citations.append(f"Section {num} of {act}")

        citations_str = ", ".join(sec_citations) if sec_citations else "applicable statutory provisions"

        return {
            "title": f"LEGAL FORMAL NOTICE ({doc_type.upper().replace('_', ' ')})",
            "sections": [
                {
                    "id": "header",
                    "title": "Parties & Header",
                    "content": f"FROM: Aggrieved Party\nTO: Counterparty ({parties})\nDATE: [Current Date]"
                },
                {
                    "id": "subject",
                    "title": "Subject Matter",
                    "content": f"LEGAL NOTICE FOR {doc_type.upper().replace('_', ' ')} REGARDING FINANCIAL/CONTRACTUAL BREACH"
                },
                {
                    "id": "facts",
                    "title": "Statement of Facts",
                    "content": f"1. The undersigned user states that: {incident}\n2. The dispute involves {amount} and relevant interactions between the parties."
                },
                {
                    "id": "legal_grounds",
                    "title": "Applicable Statutory Rights",
                    "content": f"Take notice that under {citations_str}, the undersigned is entitled to full protection and legal recourse under law."
                },
                {
                    "id": "demand",
                    "title": "Demands & Notice Period",
                    "content": f"You are hereby called upon to provide {outcome} within 15 days of receipt of this notice, failing which legal proceedings will be instituted against you."
                }
            ]
        }


# Global AI client singleton instance
ai_client = AIClient()

