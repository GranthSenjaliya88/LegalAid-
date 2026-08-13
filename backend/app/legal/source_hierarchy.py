"""
Phase 5 — Legal Source Hierarchy Engine.
Categorizes legal sources into 8 explicit hierarchy tiers:
1. Constitution / Primary Statute Act
2. Statutory Rules & Regulations
3. Government Notifications
4. Binding Judicial Precedents
5. Official Government Guidance & Circulars
6. Authority Dispute Redressal Procedures
7. Secondary References
8. LLM Parametric Memory
Ensures LLM memory NEVER overrides verified legal sources.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class SourceHierarchyInfo(BaseModel):
    tier_level: int
    tier_name: str
    source_badge: str
    authority_name: str
    is_binding: bool
    verification_url: Optional[str] = None


SOURCE_TIERS = {
    1: {"name": "Primary Statute Act", "badge": "ACT", "binding": True},
    2: {"name": "Statutory Rules & Regulations", "badge": "RULES", "binding": True},
    3: {"name": "Government Gazette Notification", "badge": "NOTIFICATION", "binding": True},
    4: {"name": "Judicial Precedent", "badge": "JUDGMENT", "binding": True},
    5: {"name": "Official Circular & Guidelines", "badge": "OFFICIAL GUIDANCE", "binding": False},
    6: {"name": "Authority Procedure", "badge": "PROCEDURE", "binding": False},
    7: {"name": "Secondary Legal Commentary", "badge": "SECONDARY", "binding": False},
    8: {"name": "AI Parametric Context", "badge": "UNVERIFIED AI", "binding": False},
}


def classify_source_tier(source_type: Optional[str], act_name: str, source_authority: Optional[str] = None, url: Optional[str] = None) -> SourceHierarchyInfo:
    """Classify legal source into standard hierarchy tier."""
    stype = (source_type or "").lower()
    aname = (act_name or "").lower()

    if "constitution" in aname or "act" in aname or "code" in aname or "sanhita" in aname or "adhiniyam" in aname:
        tier = 1
    elif "rule" in stype or "regulation" in stype:
        tier = 2
    elif "notification" in stype or "gazette" in stype:
        tier = 3
    elif "judgment" in stype or "precedent" in stype or "court" in stype:
        tier = 4
    elif "guideline" in stype or "circular" in stype or "scheme" in aname or "ombudsman" in aname:
        tier = 5
    elif "procedure" in stype or "portal" in stype:
        tier = 6
    else:
        tier = 1 if "act" in aname else 7

    tier_meta = SOURCE_TIERS[tier]
    auth = source_authority or ("Government of India" if tier <= 3 else "Official Portal")

    return SourceHierarchyInfo(
        tier_level=tier,
        tier_name=tier_meta["name"],
        source_badge=tier_meta["badge"],
        authority_name=auth,
        is_binding=tier_meta["binding"],
        verification_url=url
    )
