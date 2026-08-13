"""
Legal Corpus Search & Retrieval Engine (Phase 6).
Searches ONLY the database corpus using hybrid BM25 + controlled query expansion + state & current-law priority scoring.
Applies a strict confidence threshold — does NOT invent legal sections.
"""

import re
import json
import sqlite3
from typing import Dict, Any, List, Optional
from app.db.database import get_connection
from app.schemas.legal import RetrievalMatch, RetrievalResponseData
from app.legal.query_expansion import expand_user_query
from app.core.logging import logger

CONFIDENCE_THRESHOLD = 0.35

STOP_WORDS = {
    "the", "and", "is", "in", "to", "of", "for", "with", "a", "an", "or",
    "my", "me", "this", "that", "it", "be", "are", "from", "on", "at", "by",
    "dispute", "issue", "problem", "case", "matter", "legal", "outer", "space",
    "how", "what", "can", "get", "i", "want", "file", "against",
    "resolution", "remedy", "immediate", "claim", "opposite", "party",
    "without", "under", "where", "which"
}

LOCATION_WORDS = {
    "delhi", "mumbai", "bengaluru", "bangalore", "maharashtra", "karnataka",
    "chennai", "tamil nadu", "up", "uttar pradesh", "haryana", "gurgaon",
    "gurugram", "noida", "punjab", "gujarat", "kolkata", "west bengal", "india",
    "state", "district", "city"
}


def _normalize_hindi_hinglish(query: str, conn: sqlite3.Connection) -> List[str]:
    """Phase 11: Map Hindi / Hinglish phrases to normalized English legal terms using legal_concepts table."""
    normalized_terms = []
    q_lower = query.lower()

    try:
        rows = conn.execute("SELECT concept_key, english_synonyms_json, hindi_synonyms_json, hinglish_synonyms_json FROM legal_concepts").fetchall()
        for r in rows:
            eng = json.loads(r["english_synonyms_json"] or "[]")
            hi = json.loads(r["hindi_synonyms_json"] or "[]")
            hing = json.loads(r["hinglish_synonyms_json"] or "[]")

            all_syn = [s.lower() for s in eng + hi + hing]
            if any(syn in q_lower for syn in all_syn):
                normalized_terms.extend(eng)
    except Exception:
        pass

    return list(set(normalized_terms))


def sanitize_fts_query(query: str) -> str:
    """
    Sanitize raw user input for safe SQLite FTS5 MATCH expressions.
    Strips dangerous characters like quotes, colons, parens, asterisks,
    and reserved boolean operators (AND, OR, NOT, NEAR).
    """
    if not query:
        return ""

    cleaned = re.sub(r'[\"\':\*\(\)\{\}\[\]\^~]', ' ', query)
    
    reserved_fts_ops = {"AND", "OR", "NOT", "NEAR"}
    words = []
    for word in cleaned.split():
        clean_word = word.strip()
        if clean_word and clean_word.upper() not in reserved_fts_ops:
            words.append(f'"{clean_word}"')
            
    return " OR ".join(words[:15]) if words else ""


def search_corpus(
    domain: Optional[str],
    facts: Dict[str, Any],
    limit: int = 10
) -> RetrievalResponseData:
    """
    Execute hybrid retrieval on database corpus based on extracted facts, domain, state, and currency status.
    Uses FTS5 BM25 search + TF-IDF Vector cosine similarity fusion + concept dictionary expansion.
    """
    query_parts = []
    if facts.get("incident"):
        query_parts.append(str(facts["incident"]))
    if facts.get("desired_outcome"):
        query_parts.append(str(facts["desired_outcome"]))
    if facts.get("subdomain"):
        query_parts.append(str(facts["subdomain"]))

    combined_query = " ".join(query_parts).strip()
    if not combined_query:
        combined_query = domain or "legal provision"

    conn = get_connection()
    try:
        concept_terms = _normalize_hindi_hinglish(combined_query, conn)
        expanded_words = expand_user_query(combined_query, domain=domain or "")
        all_words = list(set(expanded_words + concept_terms))
        clean_words = [w for w in all_words if w.lower() not in STOP_WORDS]

        if not clean_words:
            clean_words = [domain] if domain else ["section"]

        fts_query = sanitize_fts_query(" ".join(clean_words[:15]))
        if not fts_query:
            fts_query = '"section"'
            
        user_state = facts.get("state")
        user_city = facts.get("city")

        matches = _query_fts(conn, fts_query=fts_query, query_words=clean_words, domain=domain, state=user_state, facts=facts, limit=limit)

        if not matches and domain and domain != "general":
            # Broaden search without strict domain filter if 0 results
            matches = _query_fts(conn, fts_query=fts_query, query_words=clean_words, domain=None, state=user_state, facts=facts, limit=limit)

        # Fallback to parameterized LIKE search if FTS returned zero matches
        if not matches:
            matches = _query_like_fallback(conn, query_words=clean_words, domain=domain, state=user_state, limit=limit)

        if not matches and domain and domain != "general":
            matches = _query_like_fallback(conn, query_words=clean_words, domain=None, state=user_state, limit=limit)

        if not matches:
            return RetrievalResponseData(
                status="insufficient_confidence",
                matches=[],
                state_verified=False,
                state_note="We couldn't verify the exact legal provision from the database corpus."
            )

        # Hybrid TF-IDF Vector Reranking
        from app.legal.vector_retriever import rank_sections_by_vector
        section_dicts = [
            {"id": idx, "title": m.title or "", "text": m.relevant_text or "", "domain": m.domain or "", "keywords": m.source_reference or ""}
            for idx, m in enumerate(matches)
        ]
        vector_scores = dict(rank_sections_by_vector(combined_query, section_dicts))

        # Re-score with Hybrid Fusion & City > State > Central Jurisdiction Hierarchy
        for idx, m in enumerate(matches):
            vec_sim = vector_scores.get(idx, 0.0)
            city_match = 1 if user_city and m.state and user_city.lower() in m.state.lower() else 0
            state_match = 1 if user_state and m.state and (m.state.lower() == user_state.lower() or m.state == "All") else 0
            
            # Combine BM25 base confidence + Vector sim + Jurisdiction rank (preserves BM25 baseline)
            fused_score = min(1.0, max(m.confidence, round(m.confidence * 0.70 + vec_sim * 0.25 + city_match * 0.10, 2)))
            m.confidence = fused_score

        # Sort matches by city match, state match, current law status, then fused confidence
        matches.sort(
            key=lambda m: (
                1 if (user_city and m.state and user_city.lower() in m.state.lower()) else 0,
                1 if (not user_state or user_state == "All" or (m.state and (m.state.lower() == user_state.lower() or m.state == "All"))) else 0,
                1 if (m.status or "").upper() in {"CURRENT", "ACTIVE"} else 0,
                m.confidence
            ),
            reverse=True
        )

        max_score = matches[0].confidence
        if max_score < CONFIDENCE_THRESHOLD:
            logger.info("Retrieval confidence %.2f below threshold %.2f", max_score, CONFIDENCE_THRESHOLD)
            return RetrievalResponseData(
                status="insufficient_confidence",
                matches=[],
                state_verified=False,
                state_note="We couldn't verify the exact legal provision from the database corpus."
            )

        # Evaluate state awareness note
        state_verified = True
        state_note = None
        if user_state and domain == "tenant":
            has_state_match = any(m.state and m.state.lower() == user_state.lower() for m in matches)
            if not has_state_match:
                state_verified = False
                state_note = f"State-specific tenancy law for '{user_state}' was not found in database. Showing Model Central Tenancy Act provisions."

        return RetrievalResponseData(
            status="success",
            matches=matches,
            state_verified=state_verified,
            state_note=state_note
        )
    finally:
        conn.close()


def _query_fts(
    conn: sqlite3.Connection,
    fts_query: str,
    query_words: List[str],
    domain: Optional[str],
    state: Optional[str],
    facts: Dict[str, Any],
    limit: int = 10
) -> List[RetrievalMatch]:
    """Execute FTS search joining acts and sections tables with state and current-law filtering."""
    params: list = [fts_query]
    domain_clause = ""

    if domain and domain in {
        "consumer", "labor", "tenant", "cyber", "criminal", "civil", "contract", "family",
        "women_rights", "children_rights", "banking", "traffic", "property", "employment_benefits",
        "constitutional", "procedural", "evidence", "sc_st_protection", "disability_rights",
        "senior_citizens", "education", "digital_online"
    }:
        domain_clause = " AND s.domain = ? "
        params.append(domain)

    state_clause = ""
    if state and state.strip() and state.strip() != "All":
        state_clause = " AND (s.state = ? OR s.state = 'All' OR s.jurisdiction = ?) "
        params.extend([state.strip(), state.strip()])

    params.append(limit * 3)

    sql = f"""
        SELECT 
            a.name AS act_name,
            a.short_name AS act_short_name,
            s.section_number,
            s.title,
            s.text,
            s.plain_language_summary,
            s.domain,
            s.subdomain,
            s.jurisdiction,
            s.state,
            COALESCE(s.status, a.status, 'CURRENT') AS status,
            s.source_name,
            s.source_url,
            COALESCE(s.official_source_url, a.official_source_url, s.source_url) AS official_source_url,
            COALESCE(s.source_authority, a.source_authority) AS source_authority,
            s.historical_reference,
            s.keywords,
            s.synonyms,
            s.last_verified,
            (a.short_name || ' Section ' || s.section_number) AS source_reference,
            fts.rank AS bm25_score
        FROM sections_fts fts
        JOIN sections s ON s.id = fts.rowid
        JOIN acts a ON a.id = s.act_id
        WHERE sections_fts MATCH ?
          AND s.is_active = 1
          AND (s.status IS NULL OR s.status = 'CURRENT' OR s.status = 'active')
          AND (s.repealed IS NULL OR s.repealed = 0)
          {domain_clause}
          {state_clause}
        ORDER BY fts.rank ASC
        LIMIT ?
    """

    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError:
        rows = []

    # If state filter or status filter yielded 0 rows, fallback without state filter
    if not rows:
        params_nostate = [fts_query]
        if domain_clause:
            params_nostate.append(domain)
        params_nostate.append(limit * 3)

        sql_nostate = f"""
            SELECT 
                a.name AS act_name,
                a.short_name AS act_short_name,
                s.section_number,
                s.title,
                s.text,
                s.plain_language_summary,
                s.domain,
                s.subdomain,
                s.jurisdiction,
                s.state,
                COALESCE(s.status, a.status, 'CURRENT') AS status,
                s.source_name,
                s.source_url,
                COALESCE(s.official_source_url, a.official_source_url, s.source_url) AS official_source_url,
                COALESCE(s.source_authority, a.source_authority) AS source_authority,
                s.historical_reference,
                s.keywords,
                s.synonyms,
                s.last_verified,
                (a.short_name || ' Section ' || s.section_number) AS source_reference,
                fts.rank AS bm25_score
            FROM sections_fts fts
            JOIN sections s ON s.id = fts.rowid
            JOIN acts a ON a.id = s.act_id
            WHERE sections_fts MATCH ?
              AND s.is_active = 1
              AND (s.status IS NULL OR s.status = 'CURRENT' OR s.status = 'active')
              AND (s.repealed IS NULL OR s.repealed = 0)
              {domain_clause}
            ORDER BY fts.rank ASC
            LIMIT ?
        """
        try:
            rows = conn.execute(sql_nostate, params_nostate).fetchall()
        except sqlite3.OperationalError:
            rows = []

    matches: List[RetrievalMatch] = []
    substantive_query_words = [w for w in query_words if w.lower() not in LOCATION_WORDS and w.lower() not in STOP_WORDS]

    for r in rows:
        full_section_text = (
            r["text"] + " " + (r["title"] or "") + " " + (r["plain_language_summary"] or "") +
            " " + (r["subdomain"] or "") + " " + (r["act_name"] or "") + " " + (r["act_short_name"] or "") +
            " " + (r["keywords"] or "") + " " + (r["synonyms"] or "")
        ).lower()

        substantive_hits = sum(1 for w in substantive_query_words if w.lower() in full_section_text)

        if substantive_query_words and substantive_hits == 0:
            continue

        keyword_ratio = substantive_hits / max(1, len(substantive_query_words))

        if domain == "general" or not domain:
            if keyword_ratio < 0.40:
                continue

        state_bonus = 0.25 if state and r["state"] and r["state"].lower() == state.lower() else 0.0
        current_law_bonus = 0.15 if (r["status"] or "").upper() in {"CURRENT", "ACTIVE"} else -0.20
        confidence = min(1.0, max(0.1, round(keyword_ratio * 0.50 + state_bonus + current_law_bonus + 0.30, 2)))

        if confidence < CONFIDENCE_THRESHOLD:
            continue

        source_ref = r["source_reference"] or f"Section {r['section_number']} of {r['act_short_name']}"
        why_applies = (
            f"Relates directly to '{r['title'] or r['subdomain'] or 'your query'}' under {r['act_short_name']}."
        )

        matches.append(RetrievalMatch(
            act=r["act_name"],
            section=r["section_number"],
            title=r["title"],
            relevant_text=r["text"],
            plain_language_summary=r["plain_language_summary"] or r["text"][:150],
            confidence=confidence,
            source_reference=source_ref,
            source_name=r["source_name"] or "Official Government Publication",
            source_url=r["source_url"] or "https://www.indiacode.nic.in",
            official_source_url=r["official_source_url"] or r["source_url"] or "https://www.indiacode.nic.in",
            source_authority=r["source_authority"] or "Government Authority",
            source_type=r["source_type"] if "source_type" in r.keys() else "Statute Act",
            historical_reference=r["historical_reference"],
            state=r["state"] or "All",
            domain=r["domain"] or "general",
            status=(r["status"] or "CURRENT").upper(),
            last_verified=r["last_verified"] or "2026-08-12",
            why_applies=why_applies
        ))

    return matches[:limit]


def _query_like_fallback(
    conn: sqlite3.Connection,
    query_words: List[str],
    domain: Optional[str],
    state: Optional[str],
    limit: int = 10
) -> List[RetrievalMatch]:
    """Safe parameterized SQL LIKE search fallback against sections and acts tables."""
    if not query_words:
        return []

    conditions = []
    params: list = []

    for w in query_words[:6]:
        pattern = f"%{w}%"
        conditions.append("(s.title LIKE ? OR s.text LIKE ? OR s.keywords LIKE ? OR s.subdomain LIKE ? OR a.name LIKE ? OR a.short_name LIKE ?)")
        params.extend([pattern, pattern, pattern, pattern, pattern, pattern])

    where_clause = " OR ".join(conditions)

    domain_clause = ""
    if domain and domain in {
        "consumer", "labor", "tenant", "cyber", "criminal", "civil", "contract", "family",
        "women_rights", "children_rights", "banking", "traffic", "property", "employment_benefits",
        "constitutional", "procedural", "evidence", "sc_st_protection", "disability_rights",
        "senior_citizens", "education", "digital_online"
    }:
        domain_clause = " AND s.domain = ? "
        params.append(domain)

    params.append(limit * 2)

    sql = f"""
        SELECT 
            a.name AS act_name,
            a.short_name AS act_short_name,
            s.section_number,
            s.title,
            s.text,
            s.plain_language_summary,
            s.domain,
            s.subdomain,
            s.jurisdiction,
            s.state,
            COALESCE(s.status, a.status, 'CURRENT') AS status,
            s.source_name,
            s.source_url,
            COALESCE(s.official_source_url, a.official_source_url, s.source_url) AS official_source_url,
            COALESCE(s.source_authority, a.source_authority) AS source_authority,
            s.historical_reference,
            s.last_verified,
            (a.short_name || ' Section ' || s.section_number) AS source_reference
        FROM sections s
        JOIN acts a ON a.id = s.act_id
        WHERE s.is_active = 1
          AND ({where_clause})
          {domain_clause}
        ORDER BY (CASE WHEN (s.status = 'CURRENT' OR s.status = 'active' OR a.status = 'CURRENT') THEN 0 ELSE 1 END) ASC, s.id ASC
        LIMIT ?
    """

    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError:
        rows = []

    matches: List[RetrievalMatch] = []
    substantive_query_words = [w for w in query_words if w.lower() not in LOCATION_WORDS and w.lower() not in STOP_WORDS]

    for r in rows:
        full_section_text = (
            r["text"] + " " + (r["title"] or "") + " " + (r["plain_language_summary"] or "") +
            " " + (r["subdomain"] or "") + " " + (r["act_name"] or "") + " " + (r["act_short_name"] or "")
        ).lower()

        substantive_hits = sum(1 for w in substantive_query_words if w.lower() in full_section_text)

        if substantive_query_words and substantive_hits == 0:
            continue

        keyword_ratio = substantive_hits / max(1, len(substantive_query_words))
        if domain == "general" or not domain:
            if keyword_ratio < 0.40:
                continue

        confidence = 0.65 if substantive_hits > 0 else 0.0

        source_ref = r["source_reference"] or f"Section {r['section_number']} of {r['act_short_name']}"
        why_applies = (
            f"Found via provision match for '{r['title'] or r['subdomain'] or 'query'}' under {r['act_short_name']}."
        )

        matches.append(RetrievalMatch(
            act=r["act_name"],
            section=r["section_number"],
            title=r["title"],
            relevant_text=r["text"],
            plain_language_summary=r["plain_language_summary"] or r["text"][:150],
            confidence=confidence,
            source_reference=source_ref,
            source_name=r["source_name"] or "Official Government Publication",
            source_url=r["source_url"] or "https://www.indiacode.nic.in",
            official_source_url=r["official_source_url"] or r["source_url"] or "https://www.indiacode.nic.in",
            source_authority=r["source_authority"] or "Government Authority",
            historical_reference=r["historical_reference"],
            state=r["state"] or "All",
            domain=r["domain"] or "general",
            status=(r["status"] or "CURRENT").upper(),
            last_verified=r["last_verified"] or "2026-08-12",
            why_applies=why_applies
        ))

    return matches


def search_bm25(db, query: str, limit: int = 20):
    from sqlalchemy import text
    sql = text(
        """
        SELECT
            section_id AS record_id,
            bm25(sections_fts) AS score
        FROM sections_fts
        WHERE sections_fts MATCH :query
        ORDER BY score
        LIMIT :limit
        """
    )

    return db.execute(
        sql,
        {
            "query": query,
            "limit": limit,
        },
    ).mappings().all()


def reciprocal_rank_fusion(
    bm25_results: list[dict],
    vector_results: list[dict],
    k: int = 60,
):
    scores = {}
    metadata = {}

    for rank, row in enumerate(bm25_results, start=1):
        record_id = row["record_id"]

        scores[record_id] = scores.get(record_id, 0.0) + (
            1.0 / (k + rank)
        )

        metadata[record_id] = {
            **metadata.get(record_id, {}),
            "bm25_score": row.get("score", 0.0),
        }

    for rank, row in enumerate(vector_results, start=1):
        record_id = row["record_id"]

        scores[record_id] = scores.get(record_id, 0.0) + (
            1.0 / (k + rank)
        )

        metadata[record_id] = {
            **metadata.get(record_id, {}),
            "vector_score": row.get("score", 0.0),
        }

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        {
            "record_id": record_id,
            "fusion_score": score,
            **metadata.get(record_id, {}),
        }
        for record_id, score in ranked
    ]
