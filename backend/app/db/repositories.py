"""
Repository operations for database models.
Handles LegalAct, LegalSection, Case, CaseFacts, and Document persistence.
"""

import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.db.models import LegalAct, LegalSection, Case, CaseFacts, DocumentModel, ExecutionTrace, ClaimAuditLog


class LegalRepository:
    """Read-only corpus access repository."""

    @staticmethod
    def get_acts(db: Session) -> List[LegalAct]:
        return db.query(LegalAct).all()

    @staticmethod
    def get_act_by_id(db: Session, act_id: int) -> Optional[LegalAct]:
        return db.query(LegalAct).filter(LegalAct.id == act_id).first()

    @staticmethod
    def get_act_by_short_name(db: Session, short_name: str) -> Optional[LegalAct]:
        return db.query(LegalAct).filter(
            LegalAct.short_name.ilike(short_name)
        ).first()

    @staticmethod
    def get_sections(db: Session, act_id: Optional[int] = None, domain: Optional[str] = None, limit: int = 100) -> List[LegalSection]:
        query = db.query(LegalSection)
        if act_id:
            query = query.filter(LegalSection.act_id == act_id)
        if domain:
            query = query.filter(LegalSection.domain == domain)
        return query.limit(limit).all()

    @staticmethod
    def get_section_by_number(db: Session, act_id: int, section_number: str) -> Optional[LegalSection]:
        return db.query(LegalSection).filter(
            LegalSection.act_id == act_id,
            LegalSection.section_number == str(section_number)
        ).first()


class CaseRepository:
    """Case intake and facts repository."""

    @staticmethod
    def create_case(db: Session, text: str, language: str = "en", session_id: Optional[str] = None) -> Case:
        case = Case(
            original_text=text,
            language=language,
            session_id=session_id,
            status="received"
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def get_case(db: Session, case_id: str) -> Optional[Case]:
        return db.query(Case).filter(Case.id == case_id).first()

    @staticmethod
    def save_classification(db: Session, case_id: str, domain: str, subdomain: str, urgency: str = "low", state: Optional[str] = None) -> Optional[Case]:
        case = db.query(Case).filter(Case.id == case_id).first()
        if case:
            case.domain = domain
            case.subdomain = subdomain
            case.urgency = urgency
            if state:
                case.state = state
            db.commit()
            db.refresh(case)
        return case

    @staticmethod
    def update_case_domain_and_status(
        db: Session,
        case_id: str,
        domain: str,
        status: str = "classified",
        subdomain: Optional[str] = None,
        state: Optional[str] = None,
        urgency: str = "low"
    ) -> Optional[Case]:
        case = db.query(Case).filter(Case.id == case_id).first()
        if case:
            case.domain = domain
            case.status = status
            if subdomain:
                case.subdomain = subdomain
            if state:
                case.state = state
            if urgency:
                case.urgency = urgency
            db.commit()
            db.refresh(case)
        return case

    @staticmethod
    def save_facts(db: Session, case_id: str, facts_dict: Dict[str, Any]) -> CaseFacts:
        facts = db.query(CaseFacts).filter(CaseFacts.case_id == case_id).first()
        if not facts:
            facts = CaseFacts(case_id=case_id)
            db.add(facts)

        for key, val in facts_dict.items():
            if hasattr(facts, key) and val is not None:
                setattr(facts, key, val)

        db.commit()
        db.refresh(facts)
        return facts

    @staticmethod
    def update_case_facts(db: Session, case_id: str, facts_dict: Dict[str, Any]) -> CaseFacts:
        return CaseRepository.save_facts(db, case_id, facts_dict)

    @staticmethod
    def delete_case(db: Session, case_id: str) -> bool:
        """
        Purge case, facts, documents, execution traces, and claim audit logs
        atomically in a single database transaction for privacy cleanup.
        """
        try:
            case = db.query(Case).filter(Case.id == case_id).first()
            if not case:
                return False

            db.query(DocumentModel).filter(DocumentModel.case_id == case_id).delete(synchronize_session=False)
            db.query(ExecutionTrace).filter(ExecutionTrace.case_id == case_id).delete(synchronize_session=False)
            db.query(ClaimAuditLog).filter(ClaimAuditLog.case_id == case_id).delete(synchronize_session=False)
            db.query(CaseFacts).filter(CaseFacts.case_id == case_id).delete(synchronize_session=False)
            db.delete(case)
            db.commit()
            return True
        except Exception:
            db.rollback()
            raise


class ExecutionTraceRepository:
    """Phase 9: Execution trace persistence and auditing."""

    @staticmethod
    def create_trace(
        db: Session,
        case_id: str,
        user_input: str,
        language: str = "en",
        extracted_facts: Optional[Dict[str, Any]] = None,
        classification: Optional[Dict[str, Any]] = None,
        jurisdiction: Optional[str] = None,
        incident_date: Optional[str] = None,
        expanded_queries: Optional[List[str]] = None,
        retrieved_records: Optional[List[Dict[str, Any]]] = None,
        selected_sources: Optional[List[Dict[str, Any]]] = None,
        generated_claims: Optional[List[Dict[str, Any]]] = None,
        audit_results: Optional[Dict[str, Any]] = None,
        final_response: Optional[Dict[str, Any]] = None
    ) -> ExecutionTrace:
        trace = ExecutionTrace(
            case_id=case_id,
            stage="pipeline",
            payload=json.dumps({
                "user_input": user_input,
                "language": language,
                "extracted_facts": extracted_facts,
                "classification": classification,
                "jurisdiction": jurisdiction,
                "incident_date": incident_date,
                "expanded_queries": expanded_queries,
                "retrieved_records": retrieved_records,
                "selected_sources": selected_sources,
                "generated_claims": generated_claims,
                "audit_results": audit_results,
                "final_response": final_response
            })
        )
        db.add(trace)
        db.commit()
        db.refresh(trace)
        return trace

    @staticmethod
    def get_traces_by_case(db: Session, case_id: str) -> List[ExecutionTrace]:
        return db.query(ExecutionTrace).filter(ExecutionTrace.case_id == case_id).all()


class DocumentRepository:
    """Document drafting and editing repository."""

    @staticmethod
    def create_document(
        db: Session,
        case_id: str,
        doc_type: str,
        title: str,
        content_sections: List[Dict[str, Any]],
        disclaimer: str,
        quality_score: float = 8.0,
        quality_warnings: Optional[List[str]] = None
    ) -> DocumentModel:
        content_str = json.dumps(content_sections) if isinstance(content_sections, (list, dict)) else str(content_sections)
        warnings_str = json.dumps(quality_warnings or []) if isinstance(quality_warnings, (list, dict)) else str(quality_warnings or "[]")

        doc = DocumentModel(
            case_id=case_id,
            type=doc_type,
            title=title,
            content_json=content_str,
            disclaimer=disclaimer,
            quality_score=quality_score,
            quality_warnings_json=warnings_str
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def get_document(db: Session, doc_id: str) -> Optional[DocumentModel]:
        return db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()

    @staticmethod
    def update_document(
        db: Session,
        doc_id: str,
        content_sections: List[Dict[str, Any]],
        title: Optional[str] = None,
        quality_score: Optional[float] = None,
        quality_warnings: Optional[List[str]] = None
    ) -> Optional[DocumentModel]:
        doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
        if doc:
            content_str = json.dumps(content_sections) if isinstance(content_sections, (list, dict)) else str(content_sections)
            doc.content_json = content_str
            if title:
                doc.title = title
            if quality_score is not None:
                doc.quality_score = quality_score
            if quality_warnings is not None:
                warnings_str = json.dumps(quality_warnings) if isinstance(quality_warnings, (list, dict)) else str(quality_warnings)
                doc.quality_warnings_json = warnings_str
            db.commit()
            db.refresh(doc)
        return doc
