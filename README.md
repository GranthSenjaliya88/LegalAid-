# LegalAId — AI Legal Rights Assistant for First-Generation Litigants in India

> **PS-04 | LegalAId: AI Legal Rights Assistant for First-Generation Litigants**

---

## 1. Problem Statement

Most people in India facing everyday legal disputes — such as a defective product refund refusal, an employer withholding severance pay, or a landlord arbitrarily cutting off essential water supply — cannot afford an advocate. 

While generic LLMs (chatbots) can attempt to answer legal questions, they frequently hallucinate non-existent statutory sections, invent fake case laws, and fail to account for state-level jurisdiction differences. 

---

## 2. Solution Overview

**LegalAId** is an AI legal rights assistant built on one fundamental principle:

# RETRIEVAL BEFORE GENERATION

The AI model is **NEVER** allowed to be the source of truth for statutory sections. Every section cited by LegalAId originates from a verified database corpus of Indian statute laws. Every citation generated passes through an 8-point verification engine before being displayed to the user.

---

## 3. Key Architecture Features

```
User Legal Case Intake (Hindi / English)
       ↓
Input Sanitization & Prompt Injection Defense
       ↓
Classifier (Domain, Subdomain, State, Urgency: Low | Medium | High | Urgent)
       ↓
State-Aware Hybrid Retrieval (SQLite FTS5 BM25 + Domain Filter + State Resolution + Current Law Check)
       ↓
Verified Candidate Statutory Provisions (FTS5 + Verified Source Metadata)
       ↓
Smart Clarification Engine (Missing Fact Ranker — Max 3 Targeted Questions)
       ↓
Rights Explainer & "Why This Law Applies" Grounded Explanation
       ↓
Advanced Citation Verifier (Validates Act, Section, Active Status, Case Context, Source Reference)
       ↓
Evidence Checklist Mapper (Interactive Document Proof Checklist)
       ↓
Action Roadmap ("What You Can Do Next" + Red Urgent Situation Warning Banner)
       ↓
Document Generator & Quality Checker (Rates Completeness 1-10 with Improvement Hints)
       ↓
Unicode ReportLab PDF Exporter (English, Hindi Devanagari, ₹ Rupee Symbol, Signature Block)
       ↓
Privacy Cleanup ("Delete My Case" Cascading Data Purge)
```

---

## 4. Why LegalAId is NOT a GPT Wrapper

1. **Retrieval-Grounded Corpus**: Statute sections are indexed in SQLite with WAL mode and FTS5 BM25 full-text search.
2. **State-Aware Jurisdiction**: Distinguishes state-specific laws (e.g. *Delhi Rent Control Act, 1958*) from central model legislation (*Model Tenancy Act, 2021*).
3. **Current-Law Versioning**: Explicitly filters and prioritizes currently active statutory frameworks (e.g., *Bharatiya Nyaya Sanhita, 2023* over historical *IPC*).
4. **Official Source Verification**: Every provision displays official government publication metadata (*India Code* links, verification date, and state applicability).
5. **Multi-Point Citation Verification**: Scrubbing engine flags or removes any claim that fails database verification.
6. **Strict Security Scoping**: User inputs are treated strictly as untrusted case facts — prompt injection instructions to invent laws are automatically neutralized.

---

## 5. Supported Domains

- **Consumer Rights** (*Consumer Protection Act, 2019*): Defective products, service deficiencies, refund disputes.
- **Labour & Employment** (*Industrial Disputes Act, 1947*): Unpaid wages, severance pay, illegal termination.
- **Tenant & Housing** (*Model Tenancy Act, 2021*, *Delhi Rent Control Act, 1958*): Security deposit withholding, illegal eviction, cutting off water/electricity.
- **Cyber Crime & Financial Fraud** (*Information Technology Act, 2000*): Unauthorized bank transfers, phishing, online fraud, RBI 72-hour zero liability guidance.
- **Criminal Rights** (*Bharatiya Nyaya Sanhita, 2023*): General civic offenses, FIR rights, basic criminal protections.

---

## 6. Test Suite Results

```text
Backend unit & pipeline tests : 17 passed
Security & PDF tests          : 3 passed
State & Domain tests          : 4 passed
-------------------------------------------
Total test suite              : 24 passed (100% success rate)
```

Command to run tests:
```bash
$env:PYTHONPATH="backend"
python -m pytest backend/tests -v
```

---

## 7. Hackathon Judge 2-Minute Demo Guide

1. **Start Backend Server**:
   ```bash
   cd backend
   python run.py
   ```
2. **Open Frontend**:
   Open `frontend/index.html` in your web browser.
3. **Click a 1-Click Real Demo Button**:
   - **Consumer Demo**: Defective washing machine refund refusal.
   - **Labor Demo**: 2 months unpaid salary demand.
   - **Tenant Demo**: Unreturned ₹20,000 security deposit in Delhi.
   - **Cyber Demo**: Unauthorized ₹25,000 bank transfer.
4. **Observe 7-Step Pipeline**:
   - **Step 1 & 2**: Situation intake & facts extraction with State detection.
   - **Step 3**: Database search returning verified citation cards with official India Code links.
   - **Step 4**: Plain-language rights explanation with "Why this law applies".
   - **Step 5**: Interactive Evidence Checklist (`[x]` / `[ ]`).
   - **Step 6**: Action Roadmap ("What You Can Do Next") + Red Urgent Alert for financial fraud/eviction.
   - **Step 7**: Document Drafting, Document Quality Rating (e.g. `8.5/10`), rich editor, and PDF download with `₹` symbol support.

---

## 8. Privacy & Security

- **Input Sanitization**: Rejects prompt injection and HTML/XSS injection.
- **No Sensitive Credentials Stored**: Password, OTP, Aadhaar, PAN inputs strictly prohibited and filtered.
- **Privacy Purge**: Clicking **"Delete My Case"** permanently removes the case, associated facts, and drafted documents from the database.

---

## 9. Limitations & Future Roadmap

- **State Expansion**: Currently pre-loaded with Delhi state tenant laws and Central statutes; future versions will expand state-specific statutes for all 28 states and 8 UTs.
- **Offline Semantic Embeddings**: FTS5 BM25 search can be augmented with local ONNX vector embeddings when hardware acceleration is available.
