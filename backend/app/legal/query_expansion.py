"""
LegalAId — Controlled Synonym & Query Expansion Engine.

Normalizes user language (English, Hindi, Hinglish) into structured legal concepts
and expands search terms for hybrid BM25 + metadata retrieval.
Does NOT generate or hallucinate new section numbers.
"""

import re
import unicodedata
from typing import List, Dict

SYNONYM_DICTIONARY: Dict[str, List[str]] = {
    # Salary / Labour / Employment
    "salary": ["wages", "unpaid wages", "remuneration", "final settlement", "tankhah", "salary not paid"],
    "wages": ["unpaid wages", "salary", "remuneration", "payment of wages", "2 working days"],
    "termination": ["retrenchment", "severance pay", "notice pay", "fired", "dismissal", "notice period"],
    "gratuity": ["continuous service", "5 years service", "gratuity payment", "resignation gratuity"],
    "maternity": ["maternity leave", "26 weeks paid leave", "pregnancy benefit"],
    "pregnancy": ["maternity benefit", "maternity leave", "nursing breaks", "creche facility"],
    "injury": ["employees compensation", "workplace accident", "employer liability", "disablement"],

    # Family / Marriage / Succession
    "divorce": ["dissolution of marriage", "mutual consent divorce", "alimony", "maintenance"],
    "alimony": ["maintenance", "permanent alimony", "interim maintenance", "litigation expenses"],
    "custody": ["child custody", "minor child", "visitation", "child maintenance"],
    "marriage": ["matrimonial relief", "divorce", "spouse", "family court"],
    "inheritance": ["succession", "intestate", "legal heir", "coparcenary", "daughter property rights"],
    "adoption": ["valid adoption", "adoptive parent", "Hindu adoption", "child adoption"],
    "talaq": ["divorce", "dissolution of marriage", "maintenance", "family court"],
    "bacche": ["child custody", "minor child", "visitation", "child maintenance"],
    "virasat": ["inheritance", "succession", "legal heir", "intestate property"],
    "dowry": ["dowry demand", "dowry prohibition", "woman property", "marriage payment"],
    "talaq": ["instant triple talaq", "Muslim woman", "subsistence allowance", "custody"],
    "guardianship": ["guardian of minor", "welfare of minor", "child custody", "guardian property"],

    # Child Protection / Education
    "pocso": ["child sexual offence", "mandatory reporting", "child statement", "special court"],
    "minor": ["child in conflict with law", "Juvenile Justice Board", "child protection", "identity privacy"],
    "juvenile": ["child in conflict with law", "Juvenile Justice Board", "Child Welfare Committee"],
    "school": ["right to education", "free education", "RTE admission", "physical punishment"],
    "education": ["right to education", "free and compulsory education", "RTE grievance"],
    "admission": ["RTE admission", "school admission denied", "weaker section quota"],
    "teacher": ["physical punishment", "mental harassment", "RTE grievance"],

    # Real Estate / Civil Remedies / Procedure
    "builder": ["promoter", "RERA", "delayed possession", "homebuyer refund"],
    "possession": ["delayed possession", "RERA refund", "allottee rights", "promoter duties"],
    "rera": ["real estate complaint", "promoter duties", "allottee rights", "homebuyer refund"],
    "injunction": ["permanent injunction", "mandatory injunction", "specific relief", "prevent breach"],
    "contract": ["specific performance", "contract enforcement", "specific relief", "agreement"],
    "limitation": ["limitation period", "condonation of delay", "late appeal", "excluded time"],
    "delay": ["condonation of delay", "limitation period", "late appeal", "sufficient cause"],
    "mediation": ["alternative dispute resolution", "settlement", "CPC section 89", "conciliation"],
    "government": ["government notice", "CPC section 80", "civil suit against government"],
    "arbitration": ["arbitration agreement", "interim measure", "arbitral award", "set aside award"],
    "insolvency": ["corporate insolvency", "operational creditor", "financial creditor", "moratorium"],

    # Access to Justice
    "lawyer": ["free legal aid", "legal services eligibility", "legal representation"],
    "advocate": ["free legal aid", "legal services authority", "legal representation"],
    "lok": ["Lok Adalat", "pre litigation settlement", "compromise", "Lok Adalat award"],

    # Tenancy / Landlord / Rent
    "deposit": ["security deposit", "deposit refund", "2 months rent", "rent control", "rental deposit"],
    "landlord": ["security deposit", "tenancy", "eviction", "rent authority", "lease agreement"],
    "evict": ["eviction", "unlawful eviction", "protection against eviction", "rent controller", "90 days notice"],
    "rent": ["tenancy agreement", "security deposit", "rent control", "rent authority"],

    # Consumer / Defective Goods / Services
    "phone": ["defective goods", "defect", "consumer", "warranty", "replacement", "refund"],
    "mobile": ["defective goods", "defect", "consumer", "warranty", "replacement", "refund"],
    "defective": ["defect", "defective goods", "quality shortcoming", "warranty", "replacement"],
    "refund": ["refusal to refund", "unfair trade practice", "deficiency in service", "e-commerce"],
    "delivered": ["deficiency in service", "non-delivery", "refund"],
    "delivery": ["deficiency in service", "non-delivery", "refund"],
    "seller": ["unfair trade practice", "product liability", "e-commerce rules", "e-daakhil"],

    # Cyber / Banking / Fraud
    "bank": ["unauthorized transaction", "rbi ombudsman", "cyber fraud", "zero liability"],
    "transfer": ["unauthorized transfer", "phishing", "cyber fraud", "66D", "rbi ombudsman"],
    "cheque": ["cheque bounce", "dishonour of cheque", "section 138", "30 days notice"],
    "otp": ["identity theft", "password theft", "section 66C", "cyber fraud"],
    "gateway": ["rbi ombudsman", "failed transaction", "bank complaint", "payment failure"],
    "forged": ["identity theft", "electronic signature", "section 66C"],

    # Criminal / Intimidation / Property Damage
    "threat": ["criminal intimidation", "threatened", "alarm", "injury", "section 351"],
    "blackmail": ["extortion", "threat", "money", "section 308"],
    "damage": ["mischief", "property damage", "destruction", "wrongful loss", "section 324"],
    "stolen": ["theft", "movable property", "without consent", "section 303"],
    "fraud": ["cheating", "deception", "misrepresentation", "section 318", "dhokhadhadi"],

    # Hinglish & Hindi Terms
    "tankhah": ["wages", "unpaid wages", "salary", "final settlement"],
    "dhamki": ["criminal intimidation", "threatened", "injury", "section 351"],
    "chori": ["theft", "movable property", "without consent", "section 303"],
    "dhokhadhadi": ["cheating", "fraud", "deception", "section 318"],
    "tod": ["mischief", "property damage", "vandalism"],
    "nikal": ["eviction", "unlawful eviction", "rent authority"],
    "electricity": ["essential supply", "withholding service", "cut off supply"],
    "rti": ["right to information", "public information officer", "information request", "first appeal"],
    "information": ["right to information", "public authority", "information request", "RTI appeal"],
    "ration": ["food security", "subsidised foodgrains", "food security allowance", "ration entitlement"],
    "aadhaar": ["identity information", "authentication", "biometric information", "data sharing"],
    "vendor": ["street vendor", "certificate of vending", "protection from eviction", "Town Vending Committee"],
    "mental": ["mental healthcare", "community living", "confidentiality", "advance directive"],
    "pollution": ["environmental pollution", "emission standard", "hazardous substance", "government directions"],
    "comments": ["sexual harassment", "unwelcome remarks", "workplace harassment"],
    "muft": ["free legal aid", "free lawyer", "legal services authority"],
    "vakil": ["lawyer", "free legal aid", "legal representation"],
}


DOMAIN_ANCHORS: Dict[str, List[str]] = {
    "labor": ["wages", "salary", "retrenchment", "final settlement"],
    "tenant": ["security deposit", "eviction", "rent control", "tenancy"],
    "consumer": ["defect", "deficiency", "unfair trade practice", "refund"],
    "cyber": ["unauthorized transaction", "cyber fraud", "identity theft"],
    "banking": ["unauthorized transaction", "bank complaint", "rbi ombudsman"],
    "criminal": ["cheating", "theft", "criminal intimidation", "mischief"],
    "family": ["marriage", "divorce", "maintenance", "child custody", "succession"],
    "children_rights": ["child protection", "mandatory reporting", "juvenile justice", "child welfare"],
    "education": ["right to education", "school admission", "free education", "RTE grievance"],
    "property": ["RERA", "promoter", "allottee", "possession", "homebuyer refund"],
    "employment_benefits": ["maternity benefit", "gratuity", "employment protection", "statutory benefit"],
    "civil": ["specific relief", "injunction", "declaration", "contract enforcement"],
    "contract": ["agreement", "specific performance", "contract enforcement", "breach"],
    "procedural": ["civil procedure", "limitation", "jurisdiction", "appeal", "mediation"],
    "healthcare": ["mental healthcare", "patient rights", "community living", "confidentiality"],
    "human_rights": ["human rights", "non-discrimination", "equality", "rights commission"],
    "public_services": ["right to information", "public authority", "food security", "government service"],
    "livelihood": ["street vendor", "certificate of vending", "livelihood protection", "eviction"],
    "environment": ["environment protection", "pollution", "hazardous substance", "emission standard"],
    "insolvency": ["corporate insolvency", "creditor", "moratorium", "resolution plan"],
    "general": ["legal services", "free legal aid", "Lok Adalat", "access to justice"],
}


def _unicode_tokens(value: str) -> List[str]:
    """Tokenize Latin and Indic text without dropping combining vowel marks."""
    tokens: List[str] = []
    current: List[str] = []
    for char in value.lower():
        category = unicodedata.category(char)
        if char == "_" or category[0] in {"L", "M", "N"}:
            current.append(char)
        elif current:
            tokens.append("".join(current))
            current = []
    if current:
        tokens.append("".join(current))
    return tokens


def expand_user_query(query_text: str, domain: str = "") -> List[str]:
    """
    Takes user prompt text and returns expanded legal keywords.
    """
    tokens = list(dict.fromkeys(_unicode_tokens(query_text)))

    expanded_terms: List[str] = []

    def add_term(term: str) -> None:
        if term and term not in expanded_terms:
            expanded_terms.append(term)

    for token in tokens:
        if len(token) > 2:
            add_term(token)
            if token in SYNONYM_DICTIONARY:
                for syn in SYNONYM_DICTIONARY[token]:
                    add_term(syn)

    # Domain-specific anchors improve recall without inventing section numbers.
    for term in DOMAIN_ANCHORS.get(domain, []):
        add_term(term)

    # Tokenize all expanded terms into clean single-word tokens for FTS5
    final_tokens: List[str] = []
    for term in expanded_terms:
        for clean_sub in _unicode_tokens(term):
            if len(clean_sub) > 2 and clean_sub not in final_tokens:
                final_tokens.append(clean_sub)

    return final_tokens
