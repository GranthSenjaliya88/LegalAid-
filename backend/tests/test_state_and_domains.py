"""
Test suite for State-Awareness, Domain Workflows, Evidence Mapper, and Action Roadmap.
"""

import pytest


def test_state_aware_tenant_retrieval(client):
    """Test state-aware retrieval prioritizes Delhi Rent Control Act when state is Delhi."""
    case_res = client.post(
        "/api/cases",
        json={"text": "My landlord in Delhi is threatening to cut off water supply.", "language": "en"}
    ).json()
    case_id = case_res["data"]["case_id"]

    classify_res = client.post(f"/api/cases/{case_id}/classify").json()
    assert classify_res["data"]["domain"] == "tenant"
    assert classify_res["data"]["facts"]["state"] == "Delhi"

    ret_res = client.post(f"/api/cases/{case_id}/retrieve").json()
    assert ret_res["success"] is True
    matches = ret_res["data"]["matches"]
    assert len(matches) > 0
    # Should include Delhi Rent Control Act Section 45
    delhi_matches = [m for m in matches if "Delhi" in m["act"] or m["state"] == "Delhi"]
    assert len(delhi_matches) > 0


def test_cyber_fraud_workflow(client):
    """Test Cyber & Financial Fraud workflow, urgency rating, and action steps."""
    case_res = client.post(
        "/api/cases",
        json={"text": "Rs 25000 was transferred from my bank account without permission via unauthorized online transfer.", "language": "en"}
    ).json()
    case_id = case_res["data"]["case_id"]

    classify_res = client.post(f"/api/cases/{case_id}/classify").json()
    assert classify_res["data"]["domain"] == "cyber"
    assert classify_res["data"]["urgency"] == "urgent"

    roadmap_res = client.get(f"/api/cases/{case_id}/roadmap").json()
    assert roadmap_res["success"] is True
    assert roadmap_res["data"]["urgency"] == "urgent"
    assert "URGENT" in roadmap_res["data"]["urgent_warning"]
    # Check step 1 includes 1930 / bank notification guidance
    assert "1930" in roadmap_res["data"]["steps"][0]["description"]


def test_evidence_checklist_generation(client):
    """Test evidence mapper produces tailored checklist for labor domain."""
    case_res = client.post(
        "/api/cases",
        json={"text": "Employer failed to pay salary for 2 months.", "language": "en"}
    ).json()
    case_id = case_res["data"]["case_id"]

    client.post(f"/api/cases/{case_id}/classify")
    ev_res = client.get(f"/api/cases/{case_id}/evidence").json()
    assert ev_res["success"] is True
    checklist = ev_res["data"]["checklist"]
    assert len(checklist) >= 3
    doc_names = [item["document_name"] for item in checklist]
    assert any("Employment Contract" in d or "Salary Slips" in d for d in doc_names)


def test_document_quality_checker(client):
    """Test document quality score evaluation and warnings output."""
    case_res = client.post(
        "/api/cases",
        json={"text": "I bought a washing machine that stopped working after two weeks.", "language": "en"}
    ).json()
    case_id = case_res["data"]["case_id"]

    client.post(f"/api/cases/{case_id}/classify")
    doc_res = client.post(f"/api/cases/{case_id}/document?doc_type=consumer_complaint").json()

    assert doc_res["success"] is True
    assert "quality_score" in doc_res["data"]
    assert isinstance(doc_res["data"]["quality_score"], float)
    assert doc_res["data"]["quality_score"] > 0
