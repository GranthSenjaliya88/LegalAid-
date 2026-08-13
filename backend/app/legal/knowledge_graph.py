"""
Statutory Knowledge Graph Engine & Linked Material Retriever.
Maps relationships between statutory codes, provisions, exceptions, remedies, and authorities.
Enforces strict validation on relationship types.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class KGRelationshipType(str, Enum):
    DEFINED_BY = "DEFINED_BY"
    RELATED_TO = "RELATED_TO"
    EXCEPTION_TO = "EXCEPTION_TO"
    REMEDIED_BY = "REMEDIED_BY"
    PROCEDURE_FOR = "PROCEDURE_FOR"
    APPLIES_TO = "APPLIES_TO"
    INTERPRETED_BY = "INTERPRETED_BY"
    SUPERSEDES = "SUPERSEDES"
    SUPERSEDED_BY = "SUPERSEDED_BY"
    CORRESPONDS_TO = "CORRESPONDS_TO"
    REPLACED_BY = "REPLACED_BY"
    SUBSUMES = "SUBSUMES"


class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # ACT, SECTION, EXCEPTION, REMEDY, AUTHORITY, RULE, PROCEDURE, JUDGMENT


class GraphEdge(BaseModel):
    source_id: str
    target_id: str
    relation_type: KGRelationshipType
    description: str


ALLOWED_RELATIONSHIPS = set(KGRelationshipType.__members__.keys())


def validate_graph_edge(edge: GraphEdge) -> bool:
    """Validate that graph relationship type is within strict allowed enum set."""
    return edge.relation_type in ALLOWED_RELATIONSHIPS


KNOWLEDGE_GRAPH_EDGES: List[GraphEdge] = [
    # Criminal Code Graph
    GraphEdge(
        source_id="bns_2023_318",
        target_id="ipc_1860_420",
        relation_type=KGRelationshipType.SUPERSEDES,
        description="BNS Section 318 supersedes IPC Section 420 for offenses post July 1, 2024."
    ),
    GraphEdge(
        source_id="bns_2023_303",
        target_id="ipc_1860_379",
        relation_type=KGRelationshipType.SUPERSEDES,
        description="BNS Section 303 supersedes IPC Section 379 for theft offenses."
    ),
    GraphEdge(
        source_id="bnss_2023_173",
        target_id="crpc_1973_154",
        relation_type=KGRelationshipType.CORRESPONDS_TO,
        description="BNSS Section 173 corresponds to CrPC Section 154 for FIR registration."
    ),

    # Consumer & Banking Graph
    GraphEdge(
        source_id="cpa_2019_35",
        target_id="cpa_2019_39",
        relation_type=KGRelationshipType.REMEDIED_BY,
        description="Section 39 defines relief/remedies awarded upon filing a complaint under Section 35."
    ),
    GraphEdge(
        source_id="rbi_ombudsman_2021",
        target_id="it_act_2000_66d",
        relation_type=KGRelationshipType.RELATED_TO,
        description="RBI Integrated Ombudsman provides banking grievance redressal for cyber financial fraud."
    ),

    # Labour & Wages Graph
    GraphEdge(
        source_id="code_on_wages_2019",
        target_id="payment_of_wages_1836",
        relation_type=KGRelationshipType.SUPERSEDES,
        description="Code on Wages 2019 repeals/subsumes Payment of Wages Act 1936."
    ),
    GraphEdge(
        source_id="ir_code_2020",
        target_id="industrial_disputes_act_1947",
        relation_type=KGRelationshipType.SUPERSEDES,
        description="Industrial Relations Code 2020 repeals/subsumes Industrial Disputes Act 1947."
    ),

    # Tenancy & Housing Graph
    GraphEdge(
        source_id="model_tenancy_act_2021",
        target_id="delhi_rent_control_act_1958",
        relation_type=KGRelationshipType.REPLACED_BY,
        description="Model Tenancy Act serves as framework for new tenancies while state rent control acts govern legacy premises."
    )
]


def get_statutory_knowledge_graph(act_name: str, section_num: Optional[str] = None) -> List[GraphEdge]:
    """Retrieve knowledge graph connections for a given Act or section."""
    aname = act_name.lower()
    results = []

    for edge in KNOWLEDGE_GRAPH_EDGES:
        if (
            aname in edge.source_id.lower() or
            aname in edge.target_id.lower() or
            aname in edge.description.lower()
        ):
            if validate_graph_edge(edge):
                results.append(edge)

    return results


def retrieve_linked_legal_material(conn, section_id: int, domain: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieve linked legal context (rules, procedures, authorities, judgments) for a retrieved section.
    """
    linked: Dict[str, List[Dict[str, Any]]] = {
        "rules": [],
        "procedures": [],
        "authorities": [],
        "judgments": []
    }
    
    try:
        rules = conn.execute("SELECT * FROM rules WHERE domain = ?", [domain]).fetchall()
        linked["rules"] = [dict(r) for r in rules]
    except Exception:
        pass

    try:
        procs = conn.execute("SELECT * FROM procedures WHERE domain = ?", [domain]).fetchall()
        linked["procedures"] = [dict(p) for p in procs]
    except Exception:
        pass

    try:
        auths = conn.execute("SELECT * FROM authorities WHERE domain = ?", [domain]).fetchall()
        linked["authorities"] = [dict(a) for a in auths]
    except Exception:
        pass

    try:
        judg = conn.execute("SELECT * FROM judgments WHERE domain = ?", [domain]).fetchall()
        linked["judgments"] = [dict(j) for j in judg]
    except Exception:
        pass

    return linked
