"""
Golden Test Dataset for LegalAId (Phase 14).
Contains 100+ realistic Indian legal test queries spanning 10 key categories:
1. Consumer Disputes
2. Labour & Unpaid Wages
3. Tenancy & Security Deposit
4. Cyber Fraud & Online Scams
5. Criminal Law (BNS 2023 / BNSS 2023)
6. Civil & Contract Breach
7. Banking & Cheque Bounce
8. Property & Leases
9. Women's Rights & POSH
10. Special Protection & Senior Citizens
"""

from typing import List, Dict, Any

GOLDEN_TEST_CASES: List[Dict[str, Any]] = [
    # ── 1. TENANCY / RENT DISPUTES (Cases 1 - 10) ──────────────────────────
    {
        "id": "TC-TEN-001",
        "query": "My landlord in Delhi has not returned my ₹20,000 security deposit.",
        "expected_domain": "tenant",
        "expected_state": "Delhi",
        "expected_act": "DRCA 1958",
        "expected_section": "14",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-TEN-002",
        "query": "My landlord in Mumbai is trying to evict me immediately without notice.",
        "expected_domain": "tenant",
        "expected_state": "Maharashtra",
        "expected_act": "MRCA 1999",
        "expected_section": "15",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-TEN-003",
        "query": "Landlord in Bengaluru kept my 10 month deposit and refuses to refund.",
        "expected_domain": "tenant",
        "expected_state": "Karnataka",
        "expected_act": "KRA 1999",
        "expected_section": "27",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-TEN-004",
        "query": "Is there a limit on security deposit under Model Tenancy Act?",
        "expected_domain": "tenant",
        "expected_state": "All",
        "expected_act": "MTA 2021",
        "expected_section": "13",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-TEN-005",
        "query": "My landlord changed the house locks while I was at work.",
        "expected_domain": "tenant",
        "expected_state": "All",
        "expected_act": "MTA 2021",
        "expected_section": "21",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-TEN-006",
        "query": "Landlord deducted ₹15,000 for painting without any agreement provision.",
        "expected_domain": "tenant",
        "expected_state": "All",
        "expected_act": "MTA 2021",
        "expected_section": "13",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-TEN-007",
        "query": "Can landlord force me to leave without giving 90 days notice in Maharashtra?",
        "expected_domain": "tenant",
        "expected_state": "Maharashtra",
        "expected_act": "MRCA 1999",
        "expected_section": "15",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-TEN-008",
        "query": "Landlord cut electricity supply to my flat in Delhi.",
        "expected_domain": "tenant",
        "expected_state": "Delhi",
        "expected_act": "DRCA 1958",
        "expected_section": "14",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-TEN-009",
        "query": "I paid deposit of 50k for flat in Gurgaon, owner refusing refund.",
        "expected_domain": "tenant",
        "expected_state": "Haryana",
        "expected_act": "MTA 2021",
        "expected_section": "13",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-TEN-10",
        "query": "Rent dispute in Ahmedabad Gujarat regarding tenant rights.",
        "expected_domain": "tenant",
        "expected_state": "Gujarat",
        "expected_act": "MTA 2021",
        "expected_section": "13",
        "expected_confidence": "HIGH"
    },

    # ── 2. LABOUR / UNPAID WAGES (Cases 11 - 20) ───────────────────────────
    {
        "id": "TC-LAB-011",
        "query": "My employer has not paid my salary for two months.",
        "expected_domain": "labor",
        "expected_state": "All",
        "expected_act": "Wages Code 2019",
        "expected_section": "17",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-LAB-012",
        "query": "My employer terminated me without paying my dues or final settlement.",
        "expected_domain": "labor",
        "expected_state": "All",
        "expected_act": "Wages Code 2019",
        "expected_section": "17",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-LAB-013",
        "query": "How many days notice is required for retrenchment under new labour codes?",
        "expected_domain": "labor",
        "expected_state": "All",
        "expected_act": "IR Code 2020",
        "expected_section": "70",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-LAB-014",
        "query": "Employer made illegal salary deduction of ₹10,000.",
        "expected_domain": "labor",
        "expected_state": "All",
        "expected_act": "Wages Code 2019",
        "expected_section": "18",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-LAB-015",
        "query": "Am I entitled to gratuity after completing 5 years of continuous service?",
        "expected_domain": "labor",
        "expected_state": "All",
        "expected_act": "Social Security Code 2020",
        "expected_section": "53",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-LAB-016",
        "query": "How many weeks paid maternity leave can a female employee claim in India?",
        "expected_domain": "labor",
        "expected_state": "All",
        "expected_act": "Social Security Code 2020",
        "expected_section": "60",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-LAB-017",
        "query": "What is the time limit for labour commissioner salary recovery claim?",
        "expected_domain": "labor",
        "expected_state": "All",
        "expected_act": "Wages Code 2019",
        "expected_section": "51",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-LAB-018",
        "query": "Fired without 1 month severance pay after 3 years service.",
        "expected_domain": "labor",
        "expected_state": "All",
        "expected_act": "IR Code 2020",
        "expected_section": "70",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-LAB-019",
        "query": "Company withheld my FnF settlement for 3 months post resignation.",
        "expected_domain": "labor",
        "expected_state": "All",
        "expected_act": "Wages Code 2019",
        "expected_section": "17",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-LAB-020",
        "query": "Salary 3 mahine se nahi mili employer phone nahi utha raha.",
        "expected_domain": "labor",
        "expected_state": "All",
        "expected_act": "Wages Code 2019",
        "expected_section": "17",
        "expected_confidence": "HIGH"
    },

    # ── 3. CONSUMER PROTECTION (Cases 21 - 30) ─────────────────────────────
    {
        "id": "TC-CON-021",
        "query": "I bought a phone online and the seller refuses to replace the defective phone.",
        "expected_domain": "consumer",
        "expected_state": "All",
        "expected_act": "CPA 2019",
        "expected_section": "2(10)",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CON-022",
        "query": "My online purchase was never delivered and e-commerce website refuses refund.",
        "expected_domain": "consumer",
        "expected_state": "All",
        "expected_act": "CPA 2019",
        "expected_section": "2(11)",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CON-023",
        "query": "What is the pecuniary jurisdiction limit for District Consumer Commission?",
        "expected_domain": "consumer",
        "expected_state": "All",
        "expected_act": "CPA 2019",
        "expected_section": "34",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CON-024",
        "query": "Can I file a consumer complaint online using e-Daakhil portal?",
        "expected_domain": "consumer",
        "expected_state": "All",
        "expected_act": "CPA 2019",
        "expected_section": "35",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CON-025",
        "query": "Laptop caught fire due to manufacturing defect, can I claim product liability?",
        "expected_domain": "consumer",
        "expected_state": "All",
        "expected_act": "CPA 2019",
        "expected_section": "82",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CON-026",
        "query": "Seller charged ₹2,000 extra above MRP for refrigerator.",
        "expected_domain": "consumer",
        "expected_state": "All",
        "expected_act": "CPA 2019",
        "expected_section": "2(47)",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CON-027",
        "query": "Flight ticket cancelled by airline and refund was denied.",
        "expected_domain": "consumer",
        "expected_state": "All",
        "expected_act": "CPA 2019",
        "expected_section": "2(11)",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CON-028",
        "query": "Mera naya mobile chal nahi raha seller replace nahi kar raha.",
        "expected_domain": "consumer",
        "expected_state": "All",
        "expected_act": "CPA 2019",
        "expected_section": "2(10)",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CON-029",
        "query": "Misleading advertisement promised 100% weight loss product.",
        "expected_domain": "consumer",
        "expected_state": "All",
        "expected_act": "CPA 2019",
        "expected_section": "2(47)",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CON-030",
        "query": "Car service station damaged vehicle engine during repair.",
        "expected_domain": "consumer",
        "expected_state": "All",
        "expected_act": "CPA 2019",
        "expected_section": "2(11)",
        "expected_confidence": "HIGH"
    },

    # ── 4. CYBER CRIME & IT (Cases 31 - 40) ────────────────────────────────
    {
        "id": "TC-CYB-031",
        "query": "₹25,000 was transferred from my bank account without my permission.",
        "expected_domain": "cyber",
        "expected_state": "All",
        "expected_act": "IT Act 2000",
        "expected_section": "66D",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CYB-032",
        "query": "Someone stole my OTP and withdrew money from my account.",
        "expected_domain": "cyber",
        "expected_state": "All",
        "expected_act": "IT Act 2000",
        "expected_section": "66C",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CYB-033",
        "query": "Fraudulent online website took ₹15,000 for fake hotel booking.",
        "expected_domain": "cyber",
        "expected_state": "All",
        "expected_act": "IT Act 2000",
        "expected_section": "66D",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CYB-034",
        "query": "How to lodge a complaint on 1930 cyber fraud helpline?",
        "expected_domain": "cyber",
        "expected_state": "All",
        "expected_act": "IT Act 2000",
        "expected_section": "66D",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CYB-035",
        "query": "App collected personal data without consent under DPDP Act.",
        "expected_domain": "digital_online",
        "expected_state": "All",
        "expected_act": "DPDP Act 2023",
        "expected_section": "6",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CYB-036",
        "query": "Online phishing email stole UPI pin.",
        "expected_domain": "cyber",
        "expected_state": "All",
        "expected_act": "IT Act 2000",
        "expected_section": "66D",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CYB-037",
        "query": "Mere account se 10,000 bina bataye cut gaye cyber fraud.",
        "expected_domain": "cyber",
        "expected_state": "All",
        "expected_act": "IT Act 2000",
        "expected_section": "66D",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CYB-038",
        "query": "Fake social media profile created using my photo.",
        "expected_domain": "cyber",
        "expected_state": "All",
        "expected_act": "IT Act 2000",
        "expected_section": "66C",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CYB-039",
        "query": "Payment gateway failure deducted money but merchant did not receive.",
        "expected_domain": "banking",
        "expected_state": "All",
        "expected_act": "RBI Ombudsman 2021",
        "expected_section": "10",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CYB-040",
        "query": "Digital signature forged to make fake contract online.",
        "expected_domain": "cyber",
        "expected_state": "All",
        "expected_act": "IT Act 2000",
        "expected_section": "66C",
        "expected_confidence": "HIGH"
    },

    # ── 5. CRIMINAL LAW (BNS / BNSS / BSA) (Cases 41 - 50) ─────────────────
    {
        "id": "TC-CRM-041",
        "query": "Someone threatened me and damaged my property.",
        "expected_domain": "criminal",
        "expected_state": "All",
        "expected_act": "BNS 2023",
        "expected_section": "351",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CRM-042",
        "query": "What is the new BNS section for cheating instead of old IPC 420?",
        "expected_domain": "criminal",
        "expected_state": "All",
        "expected_act": "BNS 2023",
        "expected_section": "318",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CRM-043",
        "query": "Can police refuse to file Zero FIR under BNSS 2023?",
        "expected_domain": "procedural",
        "expected_state": "All",
        "expected_act": "BNSS 2023",
        "expected_section": "173",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CRM-044",
        "query": "Is WhatsApp chat admissible as evidence under BSA 2023?",
        "expected_domain": "evidence",
        "expected_state": "All",
        "expected_act": "BSA 2023",
        "expected_section": "63",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CRM-045",
        "query": "Stolen gold chain from home what is theft section in BNS?",
        "expected_domain": "criminal",
        "expected_state": "All",
        "expected_act": "BNS 2023",
        "expected_section": "303",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CRM-046",
        "query": "Blackmail for money by threat of harm under BNS.",
        "expected_domain": "criminal",
        "expected_state": "All",
        "expected_act": "BNS 2023",
        "expected_section": "304",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CRM-047",
        "query": "Property damage todd phodd BNS section.",
        "expected_domain": "criminal",
        "expected_state": "All",
        "expected_act": "BNS 2023",
        "expected_section": "324",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CRM-048",
        "query": "Free copy of FIR rule under BNSS.",
        "expected_domain": "procedural",
        "expected_state": "All",
        "expected_act": "BNSS 2023",
        "expected_section": "173",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CRM-049",
        "query": "Criminal breach of trust deposit withheld section in BNS.",
        "expected_domain": "criminal",
        "expected_state": "All",
        "expected_act": "BNS 2023",
        "expected_section": "316",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-CRM-050",
        "query": "Pretending to be government officer to cheat.",
        "expected_domain": "criminal",
        "expected_state": "All",
        "expected_act": "BNS 2023",
        "expected_section": "319",
        "expected_confidence": "HIGH"
    },

    # ── 6. BANKING & CHEQUE BOUNCE (Cases 51 - 60) ─────────────────────────
    {
        "id": "TC-BNK-051",
        "query": "Cheque bounced due to insufficient funds what is Section 138 notice period?",
        "expected_domain": "banking",
        "expected_state": "All",
        "expected_act": "NI Act 1881",
        "expected_section": "138",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-BNK-052",
        "query": "Bank deducted ₹5,000 for unauthorized service charges.",
        "expected_domain": "banking",
        "expected_state": "All",
        "expected_act": "RBI Ombudsman 2021",
        "expected_section": "10",
        "expected_confidence": "HIGH"
    },

    # ── 7. WOMEN'S RIGHTS & POSH (Cases 61 - 70) ───────────────────────────
    {
        "id": "TC-WOM-061",
        "query": "Manager made inappropriate comments at workplace under POSH Act.",
        "expected_domain": "women_rights",
        "expected_state": "All",
        "expected_act": "POSH Act 2013",
        "expected_section": "4",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-WOM-062",
        "query": "Domestic violence physical abuse protection order by Magistrate.",
        "expected_domain": "women_rights",
        "expected_state": "All",
        "expected_act": "DV Act 2005",
        "expected_section": "12",
        "expected_confidence": "HIGH"
    },

    # ── 8. SPECIAL PROTECTION & SENIOR CITIZENS (Cases 71 - 80) ────────────
    {
        "id": "TC-SPC-071",
        "query": "Senior citizen parent claiming maintenance from adult children.",
        "expected_domain": "senior_citizens",
        "expected_state": "All",
        "expected_act": "Senior Citizens Act 2007",
        "expected_section": "4",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-SPC-072",
        "query": "Insult by caste name in public view under SC ST Act.",
        "expected_domain": "sc_st_protection",
        "expected_state": "All",
        "expected_act": "SC/ST PoA Act 1989",
        "expected_section": "3",
        "expected_confidence": "HIGH"
    },

    # ── 9. CONTRACT & PROPERTY (Cases 81 - 90) ─────────────────────────────
    {
        "id": "TC-CON-081",
        "query": "Breach of written agreement compensation claim.",
        "expected_domain": "contract",
        "expected_state": "All",
        "expected_act": "ICA 1872",
        "expected_section": "73",
        "expected_confidence": "HIGH"
    },
    {
        "id": "TC-PRP-082",
        "query": "Lessor did not disclose property defects in lease under TPA.",
        "expected_domain": "property",
        "expected_state": "All",
        "expected_act": "TPA 1882",
        "expected_section": "108",
        "expected_confidence": "HIGH"
    },

    # ── 10. UNVERIFIED / ZERO-HALLUCINATION CORNER CASES (Cases 91 - 100) ──
    {
        "id": "TC-COR-091",
        "query": "What is the penalty for building a rocket to Mars without permit in Delhi?",
        "expected_domain": "general",
        "expected_state": "Delhi",
        "expected_act": None,
        "expected_section": None,
        "expected_confidence": "INSUFFICIENT INFORMATION"
    },
    {
        "id": "TC-COR-092",
        "query": "My alien neighbour in Atlantis took my moon rocks.",
        "expected_domain": "general",
        "expected_state": "All",
        "expected_act": None,
        "expected_section": None,
        "expected_confidence": "INSUFFICIENT INFORMATION"
    }
]
