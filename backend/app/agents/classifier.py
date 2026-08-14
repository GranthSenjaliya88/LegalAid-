"""
LegalAId — Classifier Agent  (Step 2)

INPUT : Free-form text in Hindi or English describing a legal situation.
OUTPUT: ClassifierOutput JSON — classified_domain + extracted_facts.

Design constraints
------------------
- The LLM is used ONLY for language understanding and entity extraction.
- It MUST NOT mention any law, statute, section number, or legal judgment.
- That happens in Step 3 (Retrieval).  The classifier's job is purely:
    1. Categorise the problem domain.
    2. Pull out the relevant factual entities (parties, dates, amounts, etc.)

Fallback
--------
If GEMINI_API_KEY is not set, the module falls back to a deterministic
keyword-based classifier so the frontend / API can be developed and tested
without hitting the real LLM.  Set the env-var to switch to the real model.
"""

from __future__ import annotations

import json
import logging
import os
import re
import textwrap
from typing import Any

from app.schemas import ClassifierOutput, ExtractedFacts

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# System prompt
# ──────────────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = textwrap.dedent("""
You are the first step in a legal-rights pipeline for India.  Your ONLY job is
to understand what the user wrote and extract structured facts.  You must NOT
mention any law, statute, act, or section number, and you must NOT give any
legal opinion or judgment.  That work happens in a later step.

You will receive a message from a user in Hindi or English describing a legal
situation.  Respond with a valid JSON object — nothing else, no markdown
fences, no commentary.

Output schema (strictly):
{
  "classified_domain": "<one of: consumer | labor | tenant | other>",
  "extracted_facts": {
    "parties": "<who is involved, e.g. 'user and landlord', using the same language as the input>",
    "dates": "<any dates or time periods mentioned, or null if none>",
    "amounts": "<any money amounts mentioned, or null if none>",
    "issue_summary": "<one concise sentence describing what happened, in the user's language>",
    "user_goal": "<what the user wants: e.g. refund, compensation, notice, reinstatement, or null if unclear>"
  }
}

Domain classification rules:
- consumer  : defective product, online/offline shopping dispute, service complaint,
              unfair trade practice, failure to deliver, warranty/guarantee issue,
              overcharging, restaurant / hotel service failure
- labor     : employer not paying salary/wages/dues/notice pay/gratuity/PF/ESI,
              wrongful termination/dismissal, overtime/leave denied,
              workplace safety, employment contract dispute, maternity benefit
- tenant    : landlord–tenant dispute, rent increase, eviction threat,
              security deposit not returned, maintenance issues, lease/rent agreement
- other     : anything that doesn't clearly fit consumer, labor, or tenant;
              when in doubt choose "other" rather than forcing a guess

If any field is not clearly mentioned, set it to null.  Keep issue_summary and
user_goal short (≤ 20 words each).  Respond ONLY with the JSON object.
""").strip()


# ──────────────────────────────────────────────────────────────────────────────
# Gemini-based classifier
# ──────────────────────────────────────────────────────────────────────────────

def _call_gemini(text: str) -> ClassifierOutput:
    """Call Gemini Flash via the google-genai SDK and parse the structured JSON response."""
    from google import genai  # lazy import — optional dependency
    from google.genai import types

    api_key = os.environ["GEMINI_API_KEY"]
    client  = genai.Client(api_key=api_key)

    prompt = f"{_SYSTEM_PROMPT}\n\nUser message:\n{text}"

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )
    raw = response.text.strip() if response.text else "{}"

    # Strip accidental markdown fences if the model adds them despite the prompt
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    data: dict[str, Any] = json.loads(raw)
    return _parse_output(data)


# ──────────────────────────────────────────────────────────────────────────────
# Deterministic mock classifier (no API key required)
# ──────────────────────────────────────────────────────────────────────────────

_DOMAIN_KEYWORDS_HIGH: dict[str, list[str]] = {
    "consumer": [
        "defective", "refund", "warranty", "guarantee", "overcharg",
        "flipkart", "amazon", "meesho", "myntra", "non-delivery", "wrong item",
        "रिफंड", "दोषपूर्ण", "गारंटी", "वारंटी", "वापस",
    ],
    "labor": [
        "salary", "wage", "employer", "employee", "fired", "terminated",
        "notice pay", "gratuity", "overtime", "pf", "provident", "esi",
        "severance", "retrench", "wrongful dismissal", "maternity",
        "वेतन", "नियोक्ता", "बर्खास्त", "बोनस", "पीएफ", "ग्रैच्युटी", "मालिक",
    ],
    "tenant": [
        "landlord", "tenant", "rent", "security deposit", "deposit", "evict",
        "lease", "vacate", "eviction", "rent agreement",
        "मकान मालिक", "किराया", "जमानत", "किरायेदार", "बेदखल",
    ],
}

_DOMAIN_KEYWORDS_LOW: dict[str, list[str]] = {
    "consumer": ["product", "shop", "online", "purchase", "bought", "service", "restaurant", "hotel", "bill", "खरीद", "सामान", "उत्पाद"],
    "labor": ["leave", "job", "work", "office", "company", "नौकरी", "काम"],
    "tenant": ["flat", "house", "room", "accommodation", "maintenance", "मकान", "फ्लैट", "कमरा"],
}


def _is_hindi(text: str) -> bool:
    """Check if input text contains Devanagari script."""
    return bool(re.search(r"[\u0900-\u097F]", text))


def _mock_classify(text: str) -> ClassifierOutput:
    """
    Keyword-based fallback classifier used when GEMINI_API_KEY is absent.
    Returns plausible structure — useful for frontend/API testing.
    """
    lower = text.lower()
    scores: dict[str, int] = {d: 0 for d in ["consumer", "labor", "tenant"]}
    
    for domain, keywords in _DOMAIN_KEYWORDS_HIGH.items():
        for kw in keywords:
            if kw in lower:
                scores[domain] += 3

    for domain, keywords in _DOMAIN_KEYWORDS_LOW.items():
        for kw in keywords:
            if kw in lower:
                scores[domain] += 1

    best_domain = max(scores, key=lambda d: scores[d])
    # Require a minimum score of 3 (or at least one high-priority keyword match)
    classified = best_domain if scores[best_domain] >= 3 else "other"

    is_hi = _is_hindi(text)

    # Entity extraction from the input
    amounts = _extract_amounts(text)
    dates   = _extract_dates(text)

    facts = ExtractedFacts(
        parties=_extract_parties(text, classified, is_hi),
        dates=dates or None,
        amounts=amounts or None,
        issue_summary=text[:120].strip() + ("…" if len(text) > 120 else ""),
        user_goal=_infer_goal(lower, classified, is_hi),
    )
    return ClassifierOutput(classified_domain=classified, extracted_facts=facts)


def _extract_amounts(text: str) -> str | None:
    """Extract currency mentions from text."""
    patterns = [
        r"₹\s?[\d,]+(?:\.\d+)?",
        r"(?:rs\.?|rupees?|रुपये?|रुपए)\s?[\d,]+",
        r"[\d,]+\s?(?:rs\.?|rupees?|रुपये?|रुपए)",
    ]
    found = []
    for pat in patterns:
        found += re.findall(pat, text, re.IGNORECASE)
    return ", ".join(found) if found else None


def _extract_dates(text: str) -> str | None:
    """Extract date-like mentions from text."""
    patterns = [
        r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
        r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b",
        r"\b\d+\s+(?:days?|weeks?|months?|years?)\s+ago\b",
        r"\b(?:last|this)\s+(?:week|month|year)\b",
        r"\b\d{4}\b",
    ]
    found = []
    for pat in patterns:
        found += re.findall(pat, text, re.IGNORECASE)
    unique = list(dict.fromkeys(found))  # preserve order, deduplicate
    return ", ".join(unique[:5]) if unique else None


def _extract_parties(text: str, domain: str, is_hi: bool) -> str:
    """Infer the parties based on domain context and language."""
    if is_hi:
        defaults = {
            "consumer": "उपयोगकर्ता और विक्रेता/कंपनी",
            "labor": "उपयोगकर्ता (कर्मचारी) और नियोक्ता",
            "tenant": "उपयोगकर्ता (किराएदार) और मकान मालिक",
            "other": "उपयोगकर्ता और अन्य पक्ष",
        }
    else:
        defaults = {
            "consumer": "user and seller/company",
            "labor": "user (employee) and employer",
            "tenant": "user (tenant) and landlord",
            "other": "user and other party",
        }
    return defaults.get(domain, defaults["other"])


def _infer_goal(lower: str, domain: str, is_hi: bool) -> str | None:
    """Rough goal inference from keywords in English or Hindi."""
    if any(w in lower for w in ["salary", "wage", "dues", "pay", "वेतन", "बकाया"]):
        if domain == "labor":
            return "बकाया भुगतान (recover unpaid dues)" if is_hi else "unpaid dues recovered"
    if any(w in lower for w in ["refund", "money back", "वापस", "वापसी"]):
        return "रिफंड (refund)" if is_hi else "refund"
    if any(w in lower for w in ["compensat", "damages", "मुआवजा"]):
        return "मुआवजा (compensation)" if is_hi else "compensation"
    if any(w in lower for w in ["reinstate", "job back", "वापस नौकरी"]):
        return "पुनर्बहाली (reinstatement)" if is_hi else "reinstatement"
    if any(w in lower for w in ["notice", "नोटिस"]):
        return "कानूनी नोटिस (send legal notice)" if is_hi else "send legal notice"
    if any(w in lower for w in ["evict", "vacate", "बेदखल"]):
        return "बेदखली रोकना (prevent eviction)" if is_hi else "prevent eviction"
    
    if domain == "consumer":
        return "रिफंड या बदलाव" if is_hi else "refund or replacement"
    if domain == "labor":
        return "बकाया वेतन वापसी" if is_hi else "unpaid dues recovered"
    if domain == "tenant":
        return "जमानत राशि वापसी" if is_hi else "deposit returned"
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Schema parsing helper
# ──────────────────────────────────────────────────────────────────────────────

def _parse_output(data: dict[str, Any]) -> ClassifierOutput:
    """Validate and coerce a raw dict into ClassifierOutput."""
    valid_domains = {"consumer", "labor", "tenant", "other"}
    domain = str(data.get("classified_domain", "other")).lower()
    if domain not in valid_domains:
        domain = "other"

    raw_facts = data.get("extracted_facts") or {}
    facts = ExtractedFacts(
        parties=raw_facts.get("parties") or None,
        dates=raw_facts.get("dates") or None,
        amounts=raw_facts.get("amounts") or None,
        issue_summary=raw_facts.get("issue_summary") or None,
        user_goal=raw_facts.get("user_goal") or None,
    )
    return ClassifierOutput(classified_domain=domain, extracted_facts=facts)


# ──────────────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────────────

def classify(text: str) -> ClassifierOutput:
    """
    Classify a legal situation described in free-form Hindi or English.

    Uses Gemini Flash when GEMINI_API_KEY is set; falls back to the
    deterministic keyword classifier otherwise.
    """
    if not text or not text.strip():
        raise ValueError("Input text must not be empty.")

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if api_key:
        logger.info("classifier: using Gemini Flash")
        try:
            return _call_gemini(text)
        except Exception as exc:
            logger.warning("Gemini call failed (%s) — falling back to mock.", exc)
            return _mock_classify(text)
    else:
        logger.info("classifier: GEMINI_API_KEY not set — using mock classifier")
        return _mock_classify(text)
