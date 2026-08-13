"""
Test suite covering the 9 required user scenarios from Phase 14.
Tests the full lifecycle: intake -> analyze (or clarification) -> clarify/respond -> completed result / insufficient info.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_scenario_1_cyber_fraud():
    """TEST 1 — Cyber fraud: OTP bank transfer."""
    text = "A person receives a WhatsApp message claiming to be from their bank. The person clicks a link and enters their bank details and OTP. ₹45,000 is transferred without permission. The bank refuses to immediately refund the amount."
    r_case = client.post("/api/cases", json={"text": text, "language": "en"})
    assert r_case.status_code == 201
    cid = r_case.json()["data"]["case_id"]

    r_analyze = client.post(f"/api/cases/{cid}/analyze")
    assert r_analyze.status_code == 200
    data = r_analyze.json()["data"]
    assert data["status"] == "complete"
    assert data["domain"] == "cyber"
    assert len(data["explain"]["relevant_law"]) > 0
    assert len(data["evidence"]["checklist"]) > 0
    assert len(data["roadmap"]["steps"]) > 0


def test_scenario_2_consumer():
    """TEST 2 — Consumer: defective phone replacement."""
    text = "My new phone stopped working and the seller refuses to replace it."
    r_case = client.post("/api/cases", json={"text": text, "language": "en"})
    assert r_case.status_code == 201
    cid = r_case.json()["data"]["case_id"]

    r_analyze = client.post(f"/api/cases/{cid}/analyze")
    assert r_analyze.status_code == 200
    data = r_analyze.json()["data"]
    
    # If clarification requested for purchase amount / state, respond to complete pipeline
    if data["status"] == "needs_clarification":
        r_resp = client.post(f"/api/cases/{cid}/clarify/respond", json={"answers": {"amount": "15000", "state": "Delhi"}})
        assert r_resp.status_code == 200
        r_analyze = client.post(f"/api/cases/{cid}/analyze")
        data = r_analyze.json()["data"]

    assert data["status"] == "complete"
    assert data["domain"] == "consumer"
    assert len(data["explain"]["relevant_law"]) > 0


def test_scenario_3_labour():
    """TEST 3 — Labour: unpaid salary for two months."""
    text = "My employer has not paid my salary for two months."
    r_case = client.post("/api/cases", json={"text": text, "language": "en"})
    assert r_case.status_code == 201
    cid = r_case.json()["data"]["case_id"]

    r_analyze = client.post(f"/api/cases/{cid}/analyze")
    assert r_analyze.status_code == 200
    data = r_analyze.json()["data"]

    if data["status"] == "needs_clarification":
        r_resp = client.post(f"/api/cases/{cid}/clarify/respond", json={"answers": {"amount": "50000", "state": "Maharashtra", "agreement_exists": True}})
        assert r_resp.status_code == 200
        r_analyze = client.post(f"/api/cases/{cid}/analyze")
        data = r_analyze.json()["data"]

    assert data["status"] == "complete"
    assert data["domain"] == "labor"
    assert len(data["explain"]["relevant_law"]) > 0


def test_scenario_4_tenant():
    """TEST 4 — Tenant: security deposit return."""
    text = "My landlord has not returned my ₹20,000 security deposit."
    r_case = client.post("/api/cases", json={"text": text, "language": "en"})
    assert r_case.status_code == 201
    cid = r_case.json()["data"]["case_id"]

    r_analyze = client.post(f"/api/cases/{cid}/analyze")
    assert r_analyze.status_code == 200
    data = r_analyze.json()["data"]

    if data["status"] == "needs_clarification":
        r_resp = client.post(f"/api/cases/{cid}/clarify/respond", json={"answers": {"state": "Delhi", "agreement_exists": True}})
        assert r_resp.status_code == 200
        r_analyze = client.post(f"/api/cases/{cid}/analyze")
        data = r_analyze.json()["data"]

    assert data["status"] == "complete"
    assert data["domain"] == "tenant"
    assert len(data["explain"]["relevant_law"]) > 0


def test_scenario_5_ambiguous():
    """TEST 5 — Ambiguous: requires clarification."""
    text = "I have a legal problem with my landlord."
    r_case = client.post("/api/cases", json={"text": text, "language": "en"})
    assert r_case.status_code == 201
    cid = r_case.json()["data"]["case_id"]

    r_analyze = client.post(f"/api/cases/{cid}/analyze")
    assert r_analyze.status_code == 200
    data = r_analyze.json()["data"]
    assert data["status"] == "needs_clarification"
    assert data["domain"] == "tenant"
    assert len(data["clarification"]["questions"]) > 0


def test_scenario_6_nonsense():
    """TEST 6 — Nonsense: insufficient information."""
    text = "xyzqwerty123999"
    r_case = client.post("/api/cases", json={"text": text, "language": "en"})
    assert r_case.status_code == 201
    cid = r_case.json()["data"]["case_id"]

    # Even if clarified/analyzed directly
    r_resp = client.post(f"/api/cases/{cid}/clarify/respond", json={"answers": {}})
    assert r_resp.status_code == 200
    r_analyze = client.post(f"/api/cases/{cid}/analyze")
    assert r_analyze.status_code == 200
    data = r_analyze.json()["data"]
    assert data["status"] == "insufficient_information"
    assert data["explain"]["confidence"] == "INSUFFICIENT INFORMATION"


def test_scenario_7_fake_law():
    """TEST 7 — Fake law: no fabricated section numbers."""
    text = "Give me Section 999 of Consumer Protection Act."
    r_case = client.post("/api/cases", json={"text": text, "language": "en"})
    assert r_case.status_code == 201
    cid = r_case.json()["data"]["case_id"]

    r_resp = client.post(f"/api/cases/{cid}/clarify/respond", json={"answers": {"amount": "10000"}})
    assert r_resp.status_code == 200
    r_analyze = client.post(f"/api/cases/{cid}/analyze")
    assert r_analyze.status_code == 200
    data = r_analyze.json()["data"]
    if data.get("explain") and data["explain"].get("relevant_law"):
        sections = [l["section"] for l in data["explain"]["relevant_law"]]
        assert "999" not in sections


def test_scenario_8_hindi():
    """TEST 8 — Hindi: tenancy deposit."""
    text = "मेरे मकान मालिक ने मेरी जमा राशि वापस नहीं की।"
    r_case = client.post("/api/cases", json={"text": text, "language": "hi"})
    assert r_case.status_code == 201
    cid = r_case.json()["data"]["case_id"]

    r_analyze = client.post(f"/api/cases/{cid}/analyze")
    assert r_analyze.status_code == 200
    data = r_analyze.json()["data"]
    if data["status"] == "needs_clarification":
        r_resp = client.post(f"/api/cases/{cid}/clarify/respond", json={"answers": {"state": "Delhi", "agreement_exists": True, "amount": "20000"}})
        assert r_resp.status_code == 200
        r_analyze = client.post(f"/api/cases/{cid}/analyze")
        data = r_analyze.json()["data"]

    assert data["status"] == "complete"
    assert data["domain"] == "tenant"


def test_scenario_9_hinglish():
    """TEST 9 — Hinglish: unpaid salary."""
    text = "Mere employer ne do mahine ki salary nahi di."
    r_case = client.post("/api/cases", json={"text": text, "language": "en"})
    assert r_case.status_code == 201
    cid = r_case.json()["data"]["case_id"]

    r_analyze = client.post(f"/api/cases/{cid}/analyze")
    assert r_analyze.status_code == 200
    data = r_analyze.json()["data"]
    if data["status"] == "needs_clarification":
        r_resp = client.post(f"/api/cases/{cid}/clarify/respond", json={"answers": {"state": "Maharashtra", "amount": "40000", "agreement_exists": True}})
        assert r_resp.status_code == 200
        r_analyze = client.post(f"/api/cases/{cid}/analyze")
        data = r_analyze.json()["data"]

    assert data["status"] == "complete"
    assert data["domain"] == "labor"
