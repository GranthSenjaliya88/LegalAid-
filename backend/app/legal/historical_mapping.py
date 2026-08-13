"""
Phase 3 — Historical Law Mapping Service.
Structures transitions between historical/repealed legislation and current active statutory codes.
Supports explicit mapping types: REPLACED, SUBSUMED, CORRESPONDING, PARTIALLY_REPLACED, NO_DIRECT_EQUIVALENT.
Enforces Incident-Date awareness before picking applicable statutory provisions.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.db.models import HistoricalMapping


HISTORICAL_TRANSITION_MAP: List[Dict[str, Any]] = [
    # Criminal Code Transition (IPC 1860 -> BNS 2023)
    {
        "historical_act": "Indian Penal Code, 1860 (IPC)",
        "historical_section": "420",
        "current_act": "Bharatiya Nyaya Sanhita, 2023 (BNS)",
        "current_section": "318",
        "mapping_type": "REPLACED",
        "effective_date": "2024-07-01",
        "notes": "Cheating and dishonestly inducing delivery of property replaced by Section 318 of BNS 2023."
    },
    {
        "historical_act": "Indian Penal Code, 1860 (IPC)",
        "historical_section": "379",
        "current_act": "Bharatiya Nyaya Sanhita, 2023 (BNS)",
        "current_section": "303",
        "mapping_type": "REPLACED",
        "effective_date": "2024-07-01",
        "notes": "Theft replaced by Section 303 of BNS 2023."
    },
    {
        "historical_act": "Indian Penal Code, 1860 (IPC)",
        "historical_section": "506",
        "current_act": "Bharatiya Nyaya Sanhita, 2023 (BNS)",
        "current_section": "351",
        "mapping_type": "REPLACED",
        "effective_date": "2024-07-01",
        "notes": "Criminal intimidation replaced by Section 351 of BNS 2023."
    },

    # Procedural Transition (CrPC 1973 -> BNSS 2023)
    {
        "historical_act": "Code of Criminal Procedure, 1973 (CrPC)",
        "historical_section": "154",
        "current_act": "Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)",
        "current_section": "173",
        "mapping_type": "CORRESPONDING",
        "effective_date": "2024-07-01",
        "notes": "FIR registration and Zero FIR provisions embodied in Section 173 of BNSS 2023."
    },

    # Evidence Transition (Indian Evidence Act 1872 -> BSA 2023)
    {
        "historical_act": "Indian Evidence Act, 1872",
        "historical_section": "65B",
        "current_act": "Bharatiya Sakshya Adhiniyam, 2023 (BSA)",
        "current_section": "63",
        "mapping_type": "CORRESPONDING",
        "effective_date": "2024-07-01",
        "notes": "Electronic evidence admissibility requirements transferred from Section 65B to Section 63 of BSA 2023."
    },

    # Labour Transition (Payment of Wages Act 1936 -> Code on Wages 2019)
    {
        "historical_act": "Payment of Wages Act, 1936",
        "historical_section": "5",
        "current_act": "Code on Wages, 2019",
        "current_section": "17",
        "mapping_type": "SUBSUMED",
        "effective_date": "2020-12-30",
        "notes": "Time limit for payment of wages subsumed into Section 17 of Code on Wages 2019."
    },

    # Labour Transition (Industrial Disputes Act 1947 -> Industrial Relations Code 2020)
    {
        "historical_act": "Industrial Disputes Act, 1947 (IDA)",
        "historical_section": "25F",
        "current_act": "Industrial Relations Code, 2020",
        "current_section": "70",
        "mapping_type": "SUBSUMED",
        "effective_date": "2020-09-28",
        "notes": "Retrenchment notice and severance compensation subsumed into Section 70 of IR Code 2020."
    }
]


def resolve_historical_mapping(historical_act: str, historical_section: str) -> Optional[Dict[str, Any]]:
    """Lookup structured transition mapping for historical provisions."""
    h_act_lower = historical_act.lower()
    h_sec_lower = historical_section.lower()

    for item in HISTORICAL_TRANSITION_MAP:
        if (h_sec_lower == item["historical_section"].lower() or h_sec_lower in item["historical_section"].lower()) and (
            h_act_lower in item["historical_act"].lower() or item["historical_act"].lower() in h_act_lower
        ):
            return item
    return None


def select_applicable_statute(incident_date_str: Optional[str], current_statute: str, historical_statute: str) -> Dict[str, Any]:
    """
    Incident-Date Awareness (Directive #6 & Phase 3):
    Evaluates incident date against effective dates (e.g. 2024-07-01 for criminal codes).
    Returns applicable law version without assuming modern law always applies to past events.
    """
    if not incident_date_str:
        return {
            "applicable_law": "CURRENT",
            "statute": current_statute,
            "note": "Incident date unspecified; applying active current statutory code."
        }

    # Extract 4-digit year if present
    import re
    years = re.findall(r"\b(19\d{2}|20\d{2})\b", incident_date_str)
    if years:
        incident_year = int(years[0])
        if incident_year < 2024 and ("bns" in current_statute.lower() or "ipc" in historical_statute.lower()):
            return {
                "applicable_law": "HISTORICAL",
                "statute": historical_statute,
                "note": f"Incident occurred in {incident_year} (prior to 1st July 2024). Substantive criminal liability is governed by {historical_statute}."
            }

    return {
        "applicable_law": "CURRENT",
        "statute": current_statute,
        "note": "Incident date falls within active period of current statutory code."
    }
