from __future__ import annotations

import uuid
from datetime import date, datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import (
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    Float,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SourceType(str, Enum):
    ACT = "ACT"
    RULE = "RULE"
    REGULATION = "REGULATION"
    NOTIFICATION = "NOTIFICATION"
    CIRCULAR = "CIRCULAR"
    JUDGMENT = "JUDGMENT"
    OFFICIAL_GUIDANCE = "OFFICIAL_GUIDANCE"
    OFFICIAL_PROCEDURE = "OFFICIAL_PROCEDURE"


class LegalStatus(str, Enum):
    CURRENT = "CURRENT"
    HISTORICAL = "HISTORICAL"
    REPEALED = "REPEALED"
    SUPERSEDED = "SUPERSEDED"
    UNKNOWN = "UNKNOWN"


class CommencementStatus(str, Enum):
    NOT_COMMENCED = "NOT_COMMENCED"
    PARTIALLY_COMMENCED = "PARTIALLY_COMMENCED"
    FULLY_COMMENCED = "FULLY_COMMENCED"
    UNKNOWN = "UNKNOWN"


class BindingLevel(str, Enum):
    SUPREME_COURT_BINDING = "SUPREME_COURT_BINDING"
    HIGH_COURT_BINDING = "HIGH_COURT_BINDING"
    PERSUASIVE = "PERSUASIVE"
    OTHER = "OTHER"


class LegalSource(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    authority: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(SAEnum(SourceType), nullable=False)

    title: Mapped[str] = mapped_column(String(500), nullable=False)

    official_url: Mapped[str] = mapped_column(Text, nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(100), default="INDIA", nullable=False)

    publication_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    verification_status: Mapped[str] = mapped_column(
        String(50), default="VERIFIED", nullable=False
    )
    priority_level: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )
    version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)


class Act(Base):
    __tablename__ = "acts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    short_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    long_name: Mapped[str] = mapped_column(Text, nullable=False)

    jurisdiction: Mapped[str] = mapped_column(String(100), default="INDIA", nullable=False)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    status: Mapped[LegalStatus] = mapped_column(
        SAEnum(LegalStatus), default=LegalStatus.UNKNOWN, nullable=False
    )

    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    commencement_status: Mapped[CommencementStatus] = mapped_column(
        SAEnum(CommencementStatus),
        default=CommencementStatus.UNKNOWN,
        nullable=False,
    )

    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sources.id"), nullable=True)

    source: Mapped[Optional[LegalSource]] = relationship()
    sections: Mapped[List[Section]] = relationship(back_populates="act", cascade="all, delete-orphan")


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    act_id: Mapped[int] = mapped_column(ForeignKey("acts.id"), index=True, nullable=False)

    chapter: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    section_number: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    subsection: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    clause: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    full_text: Mapped[str] = mapped_column(Text, nullable=False)

    plain_language_summary: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    domain: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    subdomain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    status: Mapped[LegalStatus] = mapped_column(
        SAEnum(LegalStatus),
        default=LegalStatus.UNKNOWN,
        nullable=False,
    )

    commencement_status: Mapped[CommencementStatus] = mapped_column(
        SAEnum(CommencementStatus),
        default=CommencementStatus.UNKNOWN,
        nullable=False,
    )

    keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    synonyms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hindi_synonyms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hinglish_synonyms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sources.id"), nullable=True)

    act: Mapped[Act] = relationship(back_populates="sections")
    source: Mapped[Optional[LegalSource]] = relationship()


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rule_number: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    full_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    act_id: Mapped[Optional[int]] = mapped_column(ForeignKey("acts.id"), nullable=True)
    relevant_act: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    domain: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(100), default="INDIA", nullable=False)
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[LegalStatus] = mapped_column(SAEnum(LegalStatus), default=LegalStatus.CURRENT, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_authority: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    verification_status: Mapped[Optional[str]] = mapped_column(String(50), default="VERIFIED", nullable=True)
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sources.id"), nullable=True)
    source: Mapped[Optional[LegalSource]] = relationship()


class Regulation(Base):
    __tablename__ = "regulations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    regulation_number: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    full_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    issuing_authority: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(100), default="INDIA", nullable=False)
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[LegalStatus] = mapped_column(SAEnum(LegalStatus), default=LegalStatus.CURRENT, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verification_status: Mapped[Optional[str]] = mapped_column(String(50), default="VERIFIED", nullable=True)
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sources.id"), nullable=True)
    source: Mapped[Optional[LegalSource]] = relationship()


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    notification_number: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    full_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    issuing_authority: Mapped[str] = mapped_column(String(255), nullable=False)
    date_issued: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    domain: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(100), default="INDIA", nullable=False)
    status: Mapped[LegalStatus] = mapped_column(SAEnum(LegalStatus), default=LegalStatus.CURRENT, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verification_status: Mapped[Optional[str]] = mapped_column(String(50), default="VERIFIED", nullable=True)
    subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    applicable_to: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sources.id"), nullable=True)
    source: Mapped[Optional[LegalSource]] = relationship()


class LegalConcept(Base):
    __tablename__ = "legal_concepts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    concept: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    concept_key: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    domain: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    english_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hindi_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hinglish_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    english_synonyms_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hindi_synonyms_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hinglish_synonyms_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    related_acts_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Authority(Base):
    __tablename__ = "authorities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(255), default="INDIA", nullable=False)

    purpose: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    who_can_use: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    helpline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    official_portal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    online_filing_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verification_status: Mapped[Optional[str]] = mapped_column(String(50), default="VERIFIED", nullable=True)
    official_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sources.id"), nullable=True)


class Procedure(Base):
    __tablename__ = "procedures"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    authority_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("authorities.id"), nullable=True
    )

    domain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subdomain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    problem_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    right_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    authority_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    procedure_steps_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    required_documents_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    official_portal_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    follow_up_timeline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    steps: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    required_documents: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    official_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verification_status: Mapped[Optional[str]] = mapped_column(String(50), default="VERIFIED", nullable=True)
    jurisdiction: Mapped[str] = mapped_column(String(100), default="INDIA", nullable=False)
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sources.id"), nullable=True)


class Judgment(Base):
    __tablename__ = "judgments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    court: Mapped[str] = mapped_column(String(255), nullable=False)
    case_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    case_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    citation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    decision_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    facts: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    issues: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decision: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    legal_principles: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    legal_provisions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ratio_decidendi: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    act_short_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    section_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(String(100), default="general", nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verification_status: Mapped[Optional[str]] = mapped_column(String(50), default="VERIFIED", nullable=True)

    binding_level: Mapped[Optional[str]] = mapped_column(
        String(50), default="PERSUASIVE", nullable=True
    )

    jurisdiction: Mapped[str] = mapped_column(String(255), default="INDIA", nullable=False)

    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sources.id"), nullable=True)

    source: Mapped[Optional[LegalSource]] = relationship()


class HistoricalMapping(Base):
    __tablename__ = "historical_mappings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    old_act: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    old_section: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    new_act: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    new_section: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    historical_act: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    historical_section: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    current_act: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    current_section: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    effective_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    mapping_type: Mapped[str] = mapped_column(String(100), default="CORRESPONDING", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class KnowledgeGraphEdge(Base):
    __tablename__ = "knowledge_graph_edges"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    relationship: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    relation_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    target_type: Mapped[str] = mapped_column(String(100), nullable=False)
    target_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Jurisdiction(Base):
    __tablename__ = "jurisdictions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class ClaimAudit(Base):
    __tablename__ = "claim_audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    case_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    claim_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)

    source_record_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )

    source_act: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    source_section: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )

    source_url: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    support_level: Mapped[str] = mapped_column(String(50), nullable=False)
    verification_status: Mapped[str] = mapped_column(String(50), nullable=False)


class ExecutionTrace(Base):
    __tablename__ = "execution_traces"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    case_id: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, index=True
    )

    stage: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=lambda: f"case-{uuid.uuid4().hex[:12]}"
    )
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)

    domain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subdomain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    urgency: Mapped[str] = mapped_column(String(20), default="low", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    facts: Mapped[Optional[CaseFacts]] = relationship(back_populates="case", uselist=False, cascade="all, delete-orphan")


class CaseFacts(Base):
    __tablename__ = "case_facts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"), index=True, nullable=False)

    parties: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    incident: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subdomain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    amount: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    agreement_exists: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    notice_given: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    desired_outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    urgency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    additional_facts: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    case: Mapped[Case] = relationship(back_populates="facts")


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=lambda: f"doc-{uuid.uuid4().hex[:12]}"
    )
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"), index=True, nullable=False)

    type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    content_json: Mapped[str] = mapped_column(Text, nullable=False)
    disclaimer: Mapped[str] = mapped_column(Text, nullable=False)

    quality_score: Mapped[float] = mapped_column(Float, default=8.0, nullable=False)
    quality_warnings_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


# Backward compatibility aliases
LegalAct = Act
LegalSection = Section
ClaimAuditLog = ClaimAudit
