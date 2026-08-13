"""
End-to-End Pipeline Integration Test (Phase 24).
Tests the exact sequential API requests made by the frontend React application
for real citizen scenarios (Cyber, Consumer, Labour, Tenant, Hindi, Hinglish).
"""

import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def run_e2e_case_pipeline(prompt_text: str):
    # Step 1: Create Case (POST /api/cases)
    resp = client.post("/api/cases", json={"text": prompt_text})
    assert resp.status_code == 201, f"Create case failed: {resp.text}"
    case_id = resp.json()["data"]["case_id"]
    assert case_id is not None

    # Step 2: Classify (POST /api/cases/{id}/classify)
    resp = client.post(f"/api/cases/{case_id}/classify")
    assert resp.status_code == 200, f"Classify failed: {resp.text}"
    classify_data = resp.json()["data"]
    assert "domain" in classify_data

    # Step 3: Clarify (POST /api/cases/{id}/clarify)
    resp = client.post(f"/api/cases/{case_id}/clarify")
    assert resp.status_code == 200, f"Clarify failed: {resp.text}"
    clarify_data = resp.json()["data"]
    
    # If clarification requested, submit clarification response
    if clarify_data.get("needs_clarification") and clarify_data.get("questions"):
        resp = client.post(
            f"/api/cases/{case_id}/clarify/respond",
            json={"answers": {"agreement_exists": True, "notice_given": True}}
        )
        assert resp.status_code == 200, f"Clarify respond failed: {resp.text}"

    # Step 4: Explain Rights (POST /api/cases/{id}/explain)
    resp = client.post(f"/api/cases/{case_id}/explain")
    assert resp.status_code == 200, f"Explain failed: {resp.text}"
    explain_data = resp.json()["data"]
    assert "summary" in explain_data
    assert "rights" in explain_data
    assert len(explain_data["rights"]) > 0

    # Step 5: Evidence Checklist (GET /api/cases/{id}/evidence)
    resp = client.get(f"/api/cases/{case_id}/evidence")
    assert resp.status_code == 200, f"Evidence failed: {resp.text}"
    evidence_data = resp.json()["data"]
    assert "checklist" in evidence_data

    # Step 6: Action Roadmap (GET /api/cases/{id}/roadmap)
    resp = client.get(f"/api/cases/{case_id}/roadmap")
    assert resp.status_code == 200, f"Roadmap failed: {resp.text}"
    roadmap_data = resp.json()["data"]
    assert "steps" in roadmap_data

    # Step 7: Citation Verification (POST /api/cases/{id}/verify)
    resp = client.post(f"/api/cases/{case_id}/verify")
    assert resp.status_code == 200, f"Verify failed: {resp.text}"
    verify_data = resp.json()["data"]
    assert "all_verified" in verify_data or "total_citations" in verify_data or "passed" in verify_data

    return explain_data


def test_cyber_e2e_pipeline():
    prompt = (
        "A person receives a WhatsApp message claiming to be from their bank. "
        "The person clicks a link and enters their bank details and OTP. "
        "₹45,000 is then transferred from their account without permission. "
        "The bank refuses to immediately refund the amount, saying the customer shared the OTP."
    )
    explain = run_e2e_case_pipeline(prompt)
    assert explain is not None


def test_consumer_e2e_pipeline():
    prompt = "My new phone stopped working after 3 days and the seller refuses to replace or refund it."
    explain = run_e2e_case_pipeline(prompt)
    assert explain is not None


def test_labour_e2e_pipeline():
    prompt = "My employer has not paid my salary for two months and threatens to fire me."
    explain = run_e2e_case_pipeline(prompt)
    assert explain is not None


def test_tenant_e2e_pipeline():
    prompt = "My landlord has not returned my ₹20,000 security deposit despite me giving 1 month notice in Gujarat."
    explain = run_e2e_case_pipeline(prompt)
    assert explain is not None


def test_hindi_e2e_pipeline():
    prompt = "मेरे मकान मालिक ने मेरी जमा राशि वापस नहीं की और खाली करने को कह रहा है।"
    explain = run_e2e_case_pipeline(prompt)
    assert explain is not None


def test_hinglish_e2e_pipeline():
    prompt = "Mere employer ne do mahine ki salary nahi di aur bol raha hai court jao."
    explain = run_e2e_case_pipeline(prompt)
    assert explain is not None
