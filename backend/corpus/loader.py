"""
corpus/loader.py — The ONLY authorised write path to the sections table.

Ingests human-supplied JSON files in data/statutes/ into the database.
Support enhanced legal fields: subdomain, jurisdiction, state, status, source metadata.
"""

import json
import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urlparse

ALLOWED_DOMAINS = {
    "consumer", "labor", "tenant", "cyber", "criminal", "civil", "contract", "family",
    "women_rights", "children_rights", "banking", "traffic", "property", "employment_benefits",
    "constitutional", "procedural", "evidence", "sc_st_protection", "disability_rights",
    "senior_citizens", "education", "digital_online", "general", "other"
}

STATUTES_DIR = Path(__file__).parent.parent / "data" / "statutes"
OFFICIAL_SNAPSHOTS_DIR = STATUTES_DIR.parent / "official_snapshots"

OFFICIAL_SOURCE_SUFFIXES = (
    "gov.in",
    "nic.in",
    "indiacode.nic.in",
    "rbi.org.in",
    "sci.gov.in",
)


def _content_hash(value: object) -> str:
    payload = value if isinstance(value, str) else json.dumps(value, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.strip().encode("utf-8")).hexdigest()


def _is_official_source(url: str) -> bool:
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return False
    return bool(host) and any(host == suffix or host.endswith(f".{suffix}") for suffix in OFFICIAL_SOURCE_SUFFIXES)


class LoadResult(NamedTuple):
    filename: str
    act_name: str
    sections_inserted: int
    sections_skipped: int
    sections_updated: int
    errors: list[str]


def load_file(conn: sqlite3.Connection, json_path: Path, force: bool = False) -> LoadResult:
    """Ingest a single statute JSON file into the database with rich legal metadata."""
    errors: list[str] = []
    inserted = skipped = updated = 0

    raw = json_path.read_text(encoding="utf-8")
    data = json.loads(raw)

    act_data = data.get("act", {})
    sections_data = data.get("sections", [])

    for field in ("name", "short_name", "year", "domain"):
        if not act_data.get(field):
            errors.append(f"Missing act field: {field}")
    if act_data.get("domain") not in ALLOWED_DOMAINS:
        errors.append(f"Invalid domain: {act_data.get('domain')} — must be one of {ALLOWED_DOMAINS}")
    if errors:
        return LoadResult(json_path.name, act_data.get("name", "?"), 0, 0, 0, errors)

    # Upsert act
    existing_act = conn.execute(
        "SELECT id FROM acts WHERE short_name = ?", (act_data["short_name"],)
    ).fetchone()

    jurisdiction = act_data.get("jurisdiction", "India")
    source_name = act_data.get("source_name", "Official Statute Publication")
    source_url = act_data.get("source_url", "")
    official_source_url = act_data.get("official_source_url", source_url)
    source_authority = act_data.get("source_authority", "Government of India / State Gazette")
    version = act_data.get("version", "1.0")
    long_title = act_data.get("long_title", "")
    enforcement_date = act_data.get("enforcement_date", "")
    act_status = act_data.get("status", "CURRENT").upper()
    repealed_by = act_data.get("repealed_by", "")
    supersedes = act_data.get("supersedes", "")
    superseded_by = act_data.get("superseded_by", "")
    last_verified_at = act_data.get("last_verified_at", "")
    verification_status = act_data.get("verification_status", "PENDING").upper()
    act_content_hash = act_data.get("content_hash") or _content_hash(act_data)
    source_retrieved_at = act_data.get("source_retrieved_at") or datetime.now(timezone.utc).isoformat()

    if verification_status == "VERIFIED" and (not _is_official_source(official_source_url) or not last_verified_at):
        errors.append("VERIFIED act requires an official government source URL and last_verified_at")
        return LoadResult(json_path.name, act_data.get("name", "?"), 0, 0, 0, errors)

    commencement_status = act_data.get("commencement_status", "FULLY_COMMENCED")

    if existing_act:
        act_id = existing_act[0]
        if force:
            conn.execute(
                """
                UPDATE acts SET name=?, long_name=?, long_title=?, year=?, jurisdiction=?, domain=?, source_name=?, source_url=?,
                                official_source_url=?, source_authority=?, version=?, description=?, enforcement_date=?,
                                status=?, commencement_status=?, repealed_by=?, supersedes=?, superseded_by=?, last_verified_at=?, verification_status=?,
                                content_hash=?, source_retrieved_at=?
                WHERE id=?
                """,
                (
                    act_data["name"], long_title, long_title, act_data["year"], jurisdiction, act_data["domain"],
                    source_name, source_url, official_source_url, source_authority, version, act_data.get("description"),
                    enforcement_date, act_status, commencement_status, repealed_by, supersedes, superseded_by, last_verified_at, verification_status,
                    act_content_hash, source_retrieved_at,
                    act_id,
                ),
            )
    else:
        cur = conn.execute(
            """
            INSERT INTO acts(name, long_name, long_title, short_name, year, jurisdiction, domain, source_name, source_url,
                             official_source_url, source_authority, version, description, enforcement_date, status,
                             commencement_status, repealed_by, supersedes, superseded_by, last_verified_at, verification_status,
                             content_hash, source_retrieved_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                act_data["name"], long_title, long_title, act_data["short_name"], act_data["year"], jurisdiction,
                act_data["domain"], source_name, source_url, official_source_url, source_authority, version,
                act_data.get("description"), enforcement_date, act_status, commencement_status, repealed_by, supersedes, superseded_by,
                last_verified_at, verification_status, act_content_hash, source_retrieved_at
            ),
        )
        act_id = cur.lastrowid

    # Insert/update sections
    for sec in sections_data:
        sec_num = sec.get("section_number", "").strip()
        text = sec.get("text", "").strip()

        if not sec_num:
            errors.append("A section is missing section_number — skipped")
            skipped += 1
            continue
        if not text:
            errors.append(f"Section {sec_num} has empty text — skipped")
            skipped += 1
            continue

        domain = sec.get("domain", act_data["domain"])
        subdomain = sec.get("subdomain", "")
        sec_jurisdiction = sec.get("jurisdiction", jurisdiction)
        sec_state = sec.get("state", "All")
        summary = sec.get("plain_language_summary", "")
        chapter = sec.get("chapter", "")
        subsection = sec.get("subsection", "")
        clause = sec.get("clause", "")
        eff_from = sec.get("effective_from", "")
        eff_until = sec.get("effective_until", sec.get("effective_to", ""))
        eff_to = sec.get("effective_to", eff_until)
        sec_enforce_date = sec.get("enforcement_date", enforcement_date)
        sec_status = sec.get("status", act_status).upper()
        if act_status.upper() in {"HISTORICAL", "REPEALED"}:
            sec_status = act_status.upper()
        sec_repealed = 1 if sec.get("repealed", False) or sec_status in {"REPEALED", "HISTORICAL"} or act_status.upper() in {"REPEALED", "HISTORICAL"} else 0
        sec_repealed_by = sec.get("repealed_by", repealed_by)
        sec_supersedes = sec.get("supersedes", supersedes)
        sec_superseded_by = sec.get("superseded_by", superseded_by)
        hist_ref = sec.get("historical_reference", "")
        sec_src_name = sec.get("source_name", source_name)
        sec_src_url = sec.get("source_url", source_url)
        sec_off_src_url = sec.get("official_source_url", official_source_url or sec_src_url)
        sec_src_type = sec.get("source_type", "Official Gazette / India Code")
        sec_src_authority = sec.get("source_authority", source_authority)
        last_verified = sec.get("last_verified", sec.get("last_verified_at", last_verified_at))
        last_verified_at_str = sec.get("last_verified_at", last_verified)
        sec_ver_status = sec.get("verification_status", verification_status).upper()
        sec_content_hash = sec.get("content_hash") or _content_hash(text)
        sec_retrieved_at = sec.get("source_retrieved_at") or source_retrieved_at
        footnotes = sec.get("footnotes", "")

        if sec_ver_status == "VERIFIED" and (not _is_official_source(sec_off_src_url) or not last_verified_at_str):
            errors.append(f"Section {sec_num} marked VERIFIED without official provenance — skipped")
            skipped += 1
            continue

        # Store multilingual metadata as real Unicode so SQLite FTS5 can match
        # Hindi terms. Escaped ``\\uXXXX`` JSON text is not searchable as Hindi.
        keywords_json = json.dumps(sec.get("keywords", []), ensure_ascii=False)
        synonyms_json = json.dumps(sec.get("synonyms", []), ensure_ascii=False)

        existing_sec = conn.execute(
            """
            SELECT id, content_hash, text, source_url, verification_status,
                   title, plain_language_summary, subdomain, keywords, synonyms
            FROM sections WHERE act_id=? AND section_number=?
            """,
            (act_id, sec_num),
        ).fetchone()

        sec_commencement_status = sec.get("commencement_status", "FULLY_COMMENCED")

        if existing_sec:
            existing_hash = existing_sec["content_hash"] if isinstance(existing_sec, sqlite3.Row) else existing_sec[1]
            if isinstance(existing_sec, sqlite3.Row):
                stored_metadata = (
                    existing_sec["title"], existing_sec["plain_language_summary"],
                    existing_sec["subdomain"], existing_sec["keywords"], existing_sec["synonyms"],
                )
            else:
                stored_metadata = tuple(existing_sec[5:10])
            metadata_matches = stored_metadata == (
                sec.get("title"), summary, subdomain, keywords_json, synonyms_json,
            )
            if existing_hash == sec_content_hash and (not force or metadata_matches):
                skipped += 1
                continue
            if force:
                previous_text = existing_sec["text"] if isinstance(existing_sec, sqlite3.Row) else existing_sec[2]
                if previous_text:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO section_versions(
                            section_id, content_hash, full_text, source_url, retrieved_at, verification_status
                        ) VALUES (?,?,?,?,?,?)
                        """,
                        (
                            existing_sec["id"] if isinstance(existing_sec, sqlite3.Row) else existing_sec[0],
                            existing_hash or _content_hash(previous_text),
                            previous_text,
                            existing_sec["source_url"] if isinstance(existing_sec, sqlite3.Row) else existing_sec[3],
                            sec_retrieved_at,
                            (existing_sec["verification_status"] if isinstance(existing_sec, sqlite3.Row) else existing_sec[4]) or "PENDING",
                        ),
                    )
                conn.execute(
                    """
                    UPDATE sections
                    SET title=?, chapter=?, subsection=?, clause=?, text=?, plain_language_summary=?, domain=?, subdomain=?, jurisdiction=?, state=?,
                        effective_from=?, effective_until=?, effective_to=?, enforcement_date=?, status=?, commencement_status=?, repealed=?, repealed_by=?, supersedes=?,
                        superseded_by=?, historical_reference=?, source_name=?, source_url=?, official_source_url=?, source_type=?, source_authority=?,
                        last_verified=?, last_verified_at=?, verification_status=?, keywords=?, synonyms=?, full_text=?,
                        content_hash=?, source_retrieved_at=?, footnotes=?
                    WHERE id=?
                    """,
                    (
                        sec.get("title"), chapter, subsection, clause, text, summary, domain, subdomain, sec_jurisdiction, sec_state,
                        eff_from, eff_until, eff_to, sec_enforce_date, sec_status, sec_commencement_status, sec_repealed, sec_repealed_by, sec_supersedes,
                        sec_superseded_by, hist_ref, sec_src_name, sec_src_url, sec_off_src_url, sec_src_type, sec_src_authority,
                        last_verified, last_verified_at_str, sec_ver_status, keywords_json, synonyms_json, text,
                        sec_content_hash, sec_retrieved_at, footnotes,
                        existing_sec[0]
                    ),
                )
                updated += 1
            else:
                skipped += 1
        else:
            conn.execute(
                """
                INSERT INTO sections(act_id, section_number, title, chapter, subsection, clause, text, full_text, plain_language_summary, domain, subdomain, jurisdiction, state, effective_from, effective_until, effective_to, enforcement_date, status, commencement_status, repealed, repealed_by, supersedes, superseded_by, historical_reference, source_name, source_url, official_source_url, source_type, source_authority, last_verified, last_verified_at, verification_status, keywords, synonyms, content_hash, source_retrieved_at, footnotes)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    act_id, sec_num, sec.get("title"), chapter, subsection, clause, text, text, summary, domain, subdomain, sec_jurisdiction, sec_state,
                    eff_from, eff_until, eff_to, sec_enforce_date, sec_status, sec_commencement_status, sec_repealed, sec_repealed_by, sec_supersedes, sec_superseded_by,
                    hist_ref, sec_src_name, sec_src_url, sec_off_src_url, sec_src_type, sec_src_authority, last_verified, last_verified_at_str,
                    sec_ver_status, keywords_json, synonyms_json, sec_content_hash, sec_retrieved_at, footnotes
                ),
            )
            inserted += 1

    conn.commit()
    return LoadResult(json_path.name, act_data["name"], inserted, skipped, updated, errors)


def load_extended_corpus(conn: sqlite3.Connection) -> None:
    """Load additional structured legal datasets into DB tables."""
    data_dir = Path(__file__).parent.parent / "data"
    from app.legal.ingestion_pipeline import (
        ingest_rules_and_regulations,
        ingest_notifications,
        ingest_authorities_and_procedures,
        ingest_judgments,
        ingest_legal_concepts
    )

    # 1. Authorities and Procedures
    try:
        ingest_authorities_and_procedures(conn)
    except Exception as e:
        print(f"[loader] Note: authorities/procedures ingestion skipped ({e})")

    # 2. Legal Concepts
    try:
        ingest_legal_concepts(conn)
    except Exception as e:
        print(f"[loader] Note: legal concepts ingestion skipped ({e})")

    # 3. Rules & Regulations
    try:
        ingest_rules_and_regulations(conn)
    except Exception as e:
        print(f"[loader] Note: rules/regulations ingestion skipped ({e})")

    # 4. Notifications
    try:
        ingest_notifications(conn)
    except Exception as e:
        print(f"[loader] Note: notifications ingestion skipped ({e})")

    # 5. Judgments
    try:
        ingest_judgments(conn)
    except Exception as e:
        print(f"[loader] Note: judgments ingestion skipped ({e})")

    # 6. Historical Mappings
    try:
        hist_map_file = data_dir / "historical_mappings.json"
        if hist_map_file.exists():
            records = json.loads(hist_map_file.read_text(encoding="utf-8"))
            for r in records:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO historical_mappings(old_act, old_section, new_act, new_section, historical_act, historical_section, current_act, current_section, mapping_type, effective_date, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        r.get("old_act") or r.get("historical_act"),
                        r.get("old_section") or r.get("historical_section"),
                        r.get("new_act") or r.get("current_act"),
                        r.get("new_section") or r.get("current_section"),
                        r.get("historical_act", ""),
                        r.get("historical_section", ""),
                        r.get("current_act", ""),
                        r.get("current_section", ""),
                        r.get("mapping_type", "CORRESPONDING"),
                        r.get("effective_date", ""),
                        r.get("notes", "")
                    )
                )
    except Exception as e:
        print(f"[loader] Note: historical mappings ingestion skipped ({e})")

    # 7. Jurisdictions
    try:
        jur_file = data_dir / "jurisdictions.json"
        if jur_file.exists():
            records = json.loads(jur_file.read_text(encoding="utf-8"))
            for r in records:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO jurisdictions(name, level, state, district)
                    VALUES (?,?,?,?)
                    """,
                    (r["name"], r.get("level", ""), r.get("state", ""), r.get("district", ""))
                )
    except Exception as e:
        print(f"[loader] Note: jurisdictions ingestion skipped ({e})")

    # 8. Knowledge Graph
    try:
        graph_file = data_dir / "knowledge_graph.json"
        if graph_file.exists():
            records = json.loads(graph_file.read_text(encoding="utf-8"))
            for r in records:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO knowledge_graph_edges(source_type, source_id, target_type, target_id, relation_type, relationship, description, source_url)
                    VALUES (?,?,?,?,?,?,?,?)
                    """,
                    (
                        r.get("source_type", "statute"),
                        r.get("source_id", 0),
                        r.get("target_type", "statute"),
                        r.get("target_id", 0),
                        r.get("relation_type", r.get("relationship", "RELATED_TO")),
                        r.get("relationship", r.get("relation_type", "RELATED_TO")),
                        r.get("description", ""),
                        r.get("source_url", "")
                    )
                )
    except Exception as e:
        print(f"[loader] Note: knowledge graph ingestion skipped ({e})")

    conn.commit()


def load_all(
    conn: sqlite3.Connection,
    statutes_dir: Path = STATUTES_DIR,
    force: bool = False,
) -> list[LoadResult]:
    """Load every *.json file in statutes_dir and seed extended corpus tables."""
    json_files = sorted(statutes_dir.glob("*.json"))
    if not json_files:
        print(f"[loader] WARNING: No JSON files found in {statutes_dir}")
        return []

    results = []
    for f in json_files:
        print(f"[loader] Loading {f.name} ...", end=" ")
        result = load_file(conn, f, force=force)
        results.append(result)
        print(
            f"inserted={result.sections_inserted} "
            f"skipped={result.sections_skipped} "
            f"updated={result.sections_updated}"
        )
        for err in result.errors:
            print(f"  [WARN] {err}")

    load_extended_corpus(conn)
    return results


def load_official_snapshots(
    conn: sqlite3.Connection,
    snapshots_dir: Path = OFFICIAL_SNAPSHOTS_DIR,
) -> list[LoadResult]:
    """Upsert the bundled, verified official-source snapshots.

    Snapshots are local deployment assets produced by ``official_importer``.
    Loading them never performs a network request, which makes application
    startup deterministic even when the runtime filesystem is ephemeral.
    """
    snapshot_files = sorted(snapshots_dir.glob("*.official.json"))
    if not snapshot_files:
        print(f"[loader] WARNING: No official snapshots found in {snapshots_dir}")
        return []

    results = []
    for snapshot in snapshot_files:
        print(f"[loader] Loading official snapshot {snapshot.name} ...", end=" ")
        result = load_file(conn, snapshot, force=True)
        results.append(result)
        print(
            f"inserted={result.sections_inserted} "
            f"skipped={result.sections_skipped} "
            f"updated={result.sections_updated}"
        )
        for err in result.errors:
            print(f"  [WARN] {err}")
    return results


def load_production_corpus(
    conn: sqlite3.Connection,
    statutes_dir: Path = STATUTES_DIR,
    snapshots_dir: Path = OFFICIAL_SNAPSHOTS_DIR,
) -> list[LoadResult]:
    """Synchronize curated metadata and the full verified corpus at startup."""
    results = load_all(conn, statutes_dir=statutes_dir)
    results.extend(load_official_snapshots(conn, snapshots_dir=snapshots_dir))
    return results

