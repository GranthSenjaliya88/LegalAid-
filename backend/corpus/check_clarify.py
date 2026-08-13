import json
import urllib.request
from app.db.database import SessionLocal
from app.api.routes.analysis import _facts_to_dict
from app.db.repositories import CaseRepository
from app.services.clarifier import evaluate_clarification

BASE_URL = "http://127.0.0.1:8000"

def check_clarify():
    prompt = "A person receives a WhatsApp message claiming to be from their bank. The person clicks a link and enters their bank details and OTP. ₹45,000 is then transferred from their account without permission. The bank refuses to immediately refund the amount, saying the customer shared the OTP."
    
    req = urllib.request.Request(
        f"{BASE_URL}/api/cases",
        data=json.dumps({"text": prompt}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    case_id = json.loads(res.read().decode("utf-8"))["data"]["case_id"]
    
    # Classify via API
    req = urllib.request.Request(f"{BASE_URL}/api/cases/{case_id}/classify", data=b"")
    urllib.request.urlopen(req)
    
    # Direct function call check
    db = SessionLocal()
    case = CaseRepository.get_case(db, case_id)
    facts_dict = _facts_to_dict(case)
    print("CASE DOMAIN:", case.domain)
    
    res_eval = evaluate_clarification(facts_dict, domain=case.domain)
    print("DIRECT EVALUATE RESULT:", res_eval.model_dump())
    db.close()

if __name__ == "__main__":
    check_clarify()
