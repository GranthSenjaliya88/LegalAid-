"""
Official Authority Directory for LegalAId.
Provides verified government complaint portals, helplines, and filing mechanisms for legal domains.
"""

from typing import Dict, Any, List

OFFICIAL_AUTHORITIES: Dict[str, Dict[str, Any]] = {
    "consumer": {
        "authority_name": "National Consumer Helpline (NCH) & District Consumer Commission",
        "purpose": "Filing consumer complaints regarding defective goods, deficient services, or e-commerce fraud.",
        "official_url": "https://consumerhelpline.gov.in",
        "online_portal": "https://edaakhil.nic.in",
        "helpline": "1915 or 1800-11-4000",
        "type": "Central Government Portal",
        "steps": [
            "Register on National Consumer Helpline (consumerhelpline.gov.in) or call 1915.",
            "If grievance is unresolved within 30 days, file an e-complaint on e-Daakhil (edaakhil.nic.in) before the District Consumer Commission."
        ]
    },
    "cyber": {
        "authority_name": "National Cyber Crime Reporting Portal & Cyber Crime Helpline",
        "purpose": "Reporting cyber fraud, financial scams, identity theft, and unauthorized online transactions.",
        "official_url": "https://cybercrime.gov.in",
        "online_portal": "https://cybercrime.gov.in",
        "helpline": "1930 (National Cyber Financial Helpline)",
        "type": "Ministry of Home Affairs Portal",
        "steps": [
            "Call 1930 immediately within the golden hour to freeze fraudulent bank transactions.",
            "Lodge a formal incident report on cybercrime.gov.in with transaction details and screenshots."
        ]
    },
    "banking": {
        "authority_name": "Reserve Bank of India (RBI) Integrated Ombudsman",
        "purpose": "Redressal of banking grievances, unauthorized fund deductions, and payment gateway disputes.",
        "official_url": "https://cms.rbi.org.in",
        "online_portal": "https://cms.rbi.org.in",
        "helpline": "14448 (Toll Free)",
        "type": "Regulator Portal",
        "steps": [
            "First submit a written complaint to your bank branch or nodal officer.",
            "If the bank fails to resolve it within 30 days, register an online complaint at cms.rbi.org.in."
        ]
    },
    "labor": {
        "authority_name": "Office of the Labour Commissioner & SAMADHAN Portal",
        "purpose": "Filing claims for unpaid wages, illegal termination, gratuity, or maternity benefit denial.",
        "official_url": "https://samadhan.labour.gov.in",
        "online_portal": "https://samadhan.labour.gov.in",
        "helpline": "14434 (Ministry of Labour)",
        "type": "Labour Ministry Portal",
        "steps": [
            "Serve a formal written demand notice to the employer for outstanding dues.",
            "File an online dispute application on SAMADHAN portal or visit the local Labour Conciliation Officer."
        ]
    },
    "tenant": {
        "authority_name": "Rent Authority & Rent Tribunal (State Specific)",
        "purpose": "Adjudicating tenancy disputes, security deposit refund claims, and unlawful eviction notices.",
        "official_url": "https://mohua.gov.in",
        "online_portal": "https://mohua.gov.in",
        "helpline": "1800-11-6163",
        "type": "State / Municipal Rent Authority",
        "steps": [
            "Send a registered written notice demanding refund of security deposit within 15 to 30 days.",
            "Approach the local Rent Authority or Civil Court in your district if deposit is wrongfully withheld."
        ]
    },
    "women_rights": {
        "authority_name": "National Commission for Women (NCW) & Local Protection Officer",
        "purpose": "Reporting domestic violence, workplace harassment (POSH), or family safety issues.",
        "official_url": "http://ncw.nic.in",
        "online_portal": "http://ncwapps.nic.in/onlinecomplaintsubmission/",
        "helpline": "7827170170 (NCW 24x7 Helpline)",
        "type": "Statutory Commission",
        "steps": [
            "Contact the Protection Officer under the DV Act or visit the nearest police station / One Stop Centre (Sakhi).",
            "File an online complaint with the National Commission for Women (ncw.nic.in)."
        ]
    }
}


def get_official_authority(domain: str) -> Dict[str, Any]:
    """Retrieve verified official authority contact & portal details for a domain."""
    return OFFICIAL_AUTHORITIES.get(domain.lower(), OFFICIAL_AUTHORITIES["consumer"])
