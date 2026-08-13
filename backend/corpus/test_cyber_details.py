import json
import urllib.request

BASE_URL = "http://127.0.0.1:8000"

def test_details():
    prompt = "A person receives a WhatsApp message claiming to be from their bank. The person clicks a link and enters their bank details and OTP. ₹45,000 is then transferred from their account without permission. The bank refuses to immediately refund the amount, saying the customer shared the OTP."
    
    # 1. Create case
    req = urllib.request.Request(
        f"{BASE_URL}/api/cases",
        data=json.dumps({"text": prompt}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    data = json.loads(res.read().decode("utf-8"))
    case_id = data["data"]["case_id"]
    print("CREATED CASE:", case_id)
    
    # 2. Classify
    req = urllib.request.Request(f"{BASE_URL}/api/cases/{case_id}/classify", data=b"")
    res = urllib.request.urlopen(req)
    classify_data = json.loads(res.read().decode("utf-8"))
    print("CLASSIFY DATA:", json.dumps(classify_data, indent=2))
    
    # 3. Clarify
    req = urllib.request.Request(f"{BASE_URL}/api/cases/{case_id}/clarify", data=b"")
    res = urllib.request.urlopen(req)
    clarify_data = json.loads(res.read().decode("utf-8"))
    print("CLARIFY DATA:", json.dumps(clarify_data, indent=2))
    
    # 4. Explain
    req = urllib.request.Request(f"{BASE_URL}/api/cases/{case_id}/explain", data=b"")
    res = urllib.request.urlopen(req)
    explain_data = json.loads(res.read().decode("utf-8"))
    print("EXPLAIN DATA:", json.dumps(explain_data, indent=2))

if __name__ == "__main__":
    test_details()
