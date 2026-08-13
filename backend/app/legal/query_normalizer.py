from typing import Dict, List, Optional, Any


CONCEPTS: Dict[str, List[str]] = {
    "security_deposit": [
        "security deposit",
        "rental deposit",
        "deposit refund",
        "deposit not returned",
        "जमा राशि",
        "सिक्योरिटी डिपॉजिट",
        "deposit wapas",
        "deposit nahi diya",
        "security jama",
    ],

    "unpaid_wages": [
        "unpaid salary",
        "salary not paid",
        "wages not paid",
        "salary pending",
        "वेतन नहीं मिला",
        "तनख्वाह नहीं मिली",
        "salary nahi mili",
        "pagaar nahi mili",
        "tanrkha nahi mili",
    ],

    "defective_product": [
        "defective product",
        "damaged product",
        "faulty product",
        "product not working",
        "खराब सामान",
        "खराब प्रोडक्ट",
        "phone kharab",
        "product kharab hai",
        "replacement refused",
        "refund refused",
    ],

    "unauthorized_banking": [
        "unauthorized transaction",
        "money transferred without permission",
        "cyber fraud",
        "bank account debited",
        "unauthorized transfer",
        "khate se paise kat gaye",
        "paise nikal gaye",
        "bank fraud",
        "otp shared",
        "upi fraud",
        "खाते से पैसे कट गए",
    ],

    "illegal_eviction": [
        "illegal eviction",
        "forced to vacate",
        "evicted without notice",
        "landlord forcing out",
        "जबरन मकान खाली",
        "makān khālī",
        "without notice vacate",
    ],

    "domestic_violence": [
        "domestic violence",
        "husband harassment",
        "in-laws abuse",
        "workplace sexual harassment",
        "posh complaint",
        "ঘরেलू हिंसा",
        "घरेलू हिंसा",
        "ghar me harassment",
    ],

    "wrongful_termination": [
        "wrongful termination",
        "retrenchment",
        "fired without notice",
        "laid off without severance",
        "job se nikal diya",
        "fired without pay",
    ],
}


def normalize_query(query: str) -> dict:
    text = query.strip().lower()

    matched_concepts = []

    for concept, terms in CONCEPTS.items():
        for term in terms:
            if term.lower() in text:
                matched_concepts.append(concept)
                break

    expanded_terms = set()

    for concept in matched_concepts:
        expanded_terms.update(CONCEPTS[concept])

    return {
        "original": query,
        "concepts": matched_concepts,
        "expanded_terms": sorted(expanded_terms),
    }


def normalize_user_query(query: str, domain: Optional[str] = None) -> List[str]:
    """
    Backward compatibility wrapper returning expanded terms list.
    """
    normalized = normalize_query(query)
    return normalized["expanded_terms"] or [query]
