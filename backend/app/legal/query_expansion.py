"""
LegalAId — Controlled Synonym & Query Expansion Engine.

Normalizes user language (English, Hindi, Hinglish) into structured legal concepts
and expands search terms for hybrid BM25 + metadata retrieval.
Does NOT generate or hallucinate new section numbers.
"""

import re
from typing import List, Dict

SYNONYM_DICTIONARY: Dict[str, List[str]] = {
    # Salary / Labour / Employment
    "salary": ["wages", "unpaid wages", "remuneration", "final settlement", "tankhah", "salary not paid"],
    "wages": ["unpaid wages", "salary", "remuneration", "payment of wages", "2 working days"],
    "termination": ["retrenchment", "severance pay", "notice pay", "fired", "dismissal", "notice period"],
    "gratuity": ["continuous service", "5 years service", "gratuity payment", "resignation gratuity"],
    "maternity": ["maternity leave", "26 weeks paid leave", "pregnancy benefit"],

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
    "comments": ["sexual harassment", "unwelcome remarks", "workplace harassment"],
}


def expand_user_query(query_text: str, domain: str = "") -> List[str]:
    """
    Takes user prompt text and returns expanded legal keywords.
    """
    clean_text = re.sub(r"[^\w\s]", " ", query_text.lower())
    tokens = list(dict.fromkeys(clean_text.split()))

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

    # Domain specific anchor keywords
    if domain == "labor":
        domain_terms = ["wages", "salary", "retrenchment", "final settlement"]
    elif domain == "tenant":
        domain_terms = ["security deposit", "eviction", "rent control", "tenancy"]
    elif domain == "consumer":
        domain_terms = ["defect", "deficiency", "unfair trade practice", "refund"]
    elif domain == "cyber" or domain == "banking":
        domain_terms = ["unauthorized transaction", "cyber fraud", "rbi ombudsman"]
    elif domain == "criminal":
        domain_terms = ["cheating", "theft", "criminal intimidation", "mischief"]
    else:
        domain_terms = []
    for term in domain_terms:
        add_term(term)

    # Tokenize all expanded terms into clean single-word tokens for FTS5
    final_tokens: List[str] = []
    for term in expanded_terms:
        for sub_w in term.split():
            clean_sub = re.sub(r"[^\w]", "", sub_w.lower())
            if len(clean_sub) > 2 and clean_sub not in final_tokens:
                final_tokens.append(clean_sub)

    return final_tokens
