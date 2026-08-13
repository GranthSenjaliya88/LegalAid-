import json
import urllib.request

BASE_URL = "http://127.0.0.1:8000"

def test_flow():
    prompt = "A person receives a WhatsApp message claiming to be from their bank. The person clicks a link and enters their bank details and OTP. ₹45,000 is then transferred from their account without permission. The bank refuses to immediately refund the amount, saying the customer shared the OTP."
    
    print("1. Creating case...")
    req = urllib.request.Request(
        f"{BASE_URL}/api/cases",
        data=json.dumps({"text": prompt}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    data = json.loads(res.read().decode("utf-8"))
    print("Case created:", data)
    
    case_id = data["data"]["case_id"]
    
    print("\n2. Classifying case...")
    req = urllib.request.Request(
        f"{BASE_URL}/api/cases/{case_id}/classify",
        data=b"",
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    classify_data = json.loads(res.read().decode("utf-8"))
    print("Classification result:", classify_data)
    
    print("\n3. Checking clarification...")
    req = urllib.request.Request(
        f"{BASE_URL}/api/cases/{case_id}/clarify",
        data=b"",
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    clarify_data = json.loads(res.read().decode("utf-8"))
    print("Clarification result:", clarify_data)
    
    print("\n4. Explaining rights...")
    req = urllib.request.Request(
        f"{BASE_URL}/api/cases/{case_id}/explain",
        data=b"",
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    explain_data = json.loads(res.read().decode("utf-8"))
    print("Explain result:", explain_data)

if __name__ == "__main__":
    test_flow()
