"""
Centralized Source Registry Service for LegalAId.
Ensures every legal claim and provision traces back to an official Level 1 or Level 2 source.
"""

import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.db.models import SourceRegistry, LegalAct, LegalSection, LegalRule, LegalRegulation, LegalNotification, OfficialProcedure, LegalJudgment
from app.core.logging import logger

SOURCE_TYPES = {
    "ACT", "RULE", "REGULATION", "NOTIFICATION", "CIRCULAR",
    "JUDGMENT", "OFFICIAL_GUIDANCE", "OFFICIAL_PROCEDURE"
}

SOURCE_LEVELS = {
    "LEVEL_1_PRIMARY": "Primary Authority (India Code, Gazette of India, Official Govt Portals, Official Courts)",
    "LEVEL_2_PROCEDURAL": "Official Procedural Authority (RBI, Labour, Consumer, Cyber Authorities)",
    "LEVEL_3_CASELAW": "Official Judgments Repository",
    "LEVEL_4_SECONDARY": "Secondary Datasets (Evaluation / NLP Benchmarks Only)"
}


def generate_content_hash(text: str) -> str:
    """Compute SHA-256 hash of legal text for change detection."""
    clean = (text or "").strip().encode("utf-8")
    return hashlib.sha256(clean).hexdigest()


def register_source(
    db: Session,
    authority: str,
    source_type: str,
    title: str,
    official_url: Optional[str] = None,
    publication_date: Optional[str] = None,
    content_text: Optional[str] = None,
    notes: Optional[str] = None,
    version: str = "1.0"
) -> SourceRegistry:
    """
    Register or update an official source record in the Source Registry.
    Detects content changes using SHA-256 hashes.
    """
    st_upper = source_type.upper()
    if st_upper not in SOURCE_TYPES:
        st_upper = "OFFICIAL_GUIDANCE"

    content_hash = generate_content_hash(content_text or f"{authority}:{title}:{official_url}")
    today_str = datetime.utcnow().strftime("%Y-%m-%d")

    # Search for existing record by authority + title or official_url
    existing = db.query(SourceRegistry).filter(
        SourceRegistry.authority == authority,
        SourceRegistry.title == title
    ).first()

    if not existing and official_url:
        existing = db.query(SourceRegistry).filter(
            SourceRegistry.url == official_url
        ).first()

    if existing:
        if existing.content_hash != content_hash:
            logger.info("Source ID %s content hash changed (UPDATED).", existing.id)
            existing.content_hash = content_hash
            existing.last_verified_at = today_str
            existing.version = version
        else:
            existing.last_verified_at = today_str
        db.commit()
        db.refresh(existing)
        return existing

    new_source = SourceRegistry(
        authority=authority,
        source_type=st_upper,
        title=title,
        url=official_url or "",
        publication_date=publication_date or today_str,
        retrieved_at=today_str,
        last_verified_at=today_str,
        content_hash=content_hash,
        verification_status="VERIFIED",
        version=version,
        notes=notes
    )
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return new_source


def get_source_by_id(db: Session, source_id: int) -> Optional[SourceRegistry]:
    """Fetch source record by ID."""
    return db.query(SourceRegistry).filter(SourceRegistry.id == source_id).first()


def list_verified_sources(db: Session, limit: int = 100) -> List[SourceRegistry]:
    """Fetch verified sources for audit & reporting."""
    return db.query(SourceRegistry).filter(
        SourceRegistry.verification_status == "VERIFIED"
    ).limit(limit).all()
