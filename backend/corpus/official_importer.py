"""Bulk ingestion from official India Code act pages.

The importer deliberately accepts only allow-listed government hosts, records a
content hash for every provision, keeps the raw official URL on every row, and
routes writes through :mod:`corpus.loader`.  It never asks an LLM to create or
complete statutory text.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import parse_qs, urljoin, urlparse

import httpx

from corpus.loader import OFFICIAL_SOURCE_SUFFIXES, STATUTES_DIR, load_file


INDIA_CODE_ORIGIN = "https://www.indiacode.nic.in"
DEFAULT_SNAPSHOT_DIR = STATUTES_DIR.parent / "official_snapshots"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def _official_url(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return bool(host) and any(host == suffix or host.endswith(f".{suffix}") for suffix in OFFICIAL_SOURCE_SUFFIXES)


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag.lower() in {"br", "p", "div", "li", "hr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"p", "div", "li"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        value = "".join(self.parts).replace("\xa0", " ")
        value = re.sub(r"[ \t]+", " ", value)
        value = re.sub(r"\s*\n\s*", "\n", value)
        value = re.sub(r"\n{3,}", "\n\n", value)
        return value.strip()


def html_to_text(value: str) -> str:
    parser = _TextExtractor()
    parser.feed(value or "")
    parser.close()
    return parser.text()


def _page_title(page_html: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", page_html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    title = html_to_text(match.group(1))
    return re.sub(r"^India\s+Code:\s*", "", title, flags=re.IGNORECASE).strip()


def _title_similarity(expected: str, actual: str) -> float:
    ignored = {"the", "of"}
    expected_tokens = {
        token for token in re.findall(r"[a-z0-9]+", expected.lower()) if token not in ignored
    }
    actual_tokens = {
        token for token in re.findall(r"[a-z0-9]+", actual.lower()) if token not in ignored
    }
    union = expected_tokens | actual_tokens
    return len(expected_tokens & actual_tokens) / max(1, len(union))


def extract_numbered_subsection(text: str, marker: str) -> str:
    """Extract a top-level numbered definition such as ``(10)`` from official text."""
    if not marker.isdigit():
        return ""
    start = re.search(rf"(?m)^\({re.escape(marker)}\)\s+", text)
    if not start:
        return ""
    next_marker = re.search(r"(?m)^\(\d+\)\s+", text[start.end():])
    end = start.end() + next_marker.start() if next_marker else len(text)
    return text[start.start():end].strip()


def _derive_curated_subsections(fetched: list[dict], curated_sections: dict[str, dict]) -> list[dict]:
    official_numbers = {str(section.get("section_number")) for section in fetched}
    parents = {str(section.get("section_number")): section for section in fetched}
    derived: list[dict] = []
    for number, curated in curated_sections.items():
        if number in official_numbers:
            continue
        match = re.fullmatch(r"([^()]+)\((\d+)\)", number)
        if not match:
            continue
        parent = parents.get(match.group(1))
        if not parent:
            continue
        excerpt = extract_numbered_subsection(str(parent.get("text") or ""), match.group(2))
        if not excerpt:
            continue
        derived.append(
            {
                **parent,
                "section_number": number,
                "title": curated.get("title") or f"Section {number}",
                "text": excerpt,
                "full_text": excerpt,
                "footnotes": "",
                "content_hash": _sha256(excerpt),
            }
        )
    return derived


@dataclass(frozen=True)
class SectionLink:
    section_id: str
    section_number: str
    order: int
    act_id: str
    url: str
    title: str


class _ActPageParser(HTMLParser):
    def __init__(self, page_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.page_url = page_url
        self.links: list[SectionLink] = []
        self._current: Optional[dict[str, object]] = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href") or ""
        # India Code emits unescaped ``&sectionId`` attributes. Python's HTML
        # parser interprets ``&sect`` as the section-sign entity, so restore
        # the intended query parameter before parsing it.
        href = href.replace("§ionId", "&sectionId").replace("§ionno", "&sectionno")
        if "show-data?" not in href or "sectionId=" not in href:
            return
        absolute = urljoin(self.page_url, href)
        query = parse_qs(urlparse(absolute).query)
        section_id = (query.get("sectionId") or query.get("sectionID") or [""])[0]
        section_number = (query.get("sectionno") or [""])[0]
        act_id = (query.get("actid") or [""])[0]
        try:
            order = int((query.get("orderno") or ["0"])[0])
        except ValueError:
            order = 0
        if section_id and act_id:
            self._current = {
                "section_id": section_id,
                "section_number": section_number,
                "order": order,
                "act_id": act_id,
                "url": absolute,
                "text": [],
            }

    def handle_data(self, data: str) -> None:
        if self._current is not None:
            self._current["text"].append(data)  # type: ignore[index,union-attr]

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._current is None:
            return
        raw_title = re.sub(r"\s+", " ", "".join(self._current["text"])).strip()  # type: ignore[arg-type]
        number = str(self._current["section_number"] or "").strip()
        if not number:
            match = re.match(r"Section\s+([^.]*)\.?", raw_title, flags=re.IGNORECASE)
            number = match.group(1).strip() if match else str(self._current["order"])
        title = re.sub(rf"^Section\s+{re.escape(number)}\.?\s*", "", raw_title, flags=re.IGNORECASE).strip()
        self.links.append(
            SectionLink(
                section_id=str(self._current["section_id"]),
                section_number=number,
                order=int(self._current["order"]),
                act_id=str(self._current["act_id"]),
                url=str(self._current["url"]),
                title=title or f"Section {number}",
            )
        )
        self._current = None


def parse_section_links(page_html: str, page_url: str) -> list[SectionLink]:
    parser = _ActPageParser(page_url)
    parser.feed(page_html)
    parser.close()
    unique: dict[tuple[str, str], SectionLink] = {}
    for link in parser.links:
        unique[(link.section_id, link.section_number)] = link
    return sorted(unique.values(), key=lambda item: (item.order, item.section_number))


@dataclass(frozen=True)
class ActImportSpec:
    curated_path: Path
    act: dict
    page_url: str

    @property
    def short_name(self) -> str:
        return str(self.act["short_name"])

    @property
    def domain(self) -> str:
        return str(self.act["domain"])


@dataclass
class ImportSummary:
    acts_discovered: int = 0
    sections_discovered: int = 0
    sections_inserted: int = 0
    sections_updated: int = 0
    sections_unchanged: int = 0
    sections_rejected: int = 0
    failures: int = 0


class IndiaCodeClient:
    def __init__(self, workers: int = 4, timeout: float = 30.0, retries: int = 3) -> None:
        self.workers = max(1, min(workers, 8))
        self.retries = max(1, retries)
        self.client = httpx.Client(
            follow_redirects=True,
            timeout=timeout,
            headers={"User-Agent": "LegalAId-Official-Corpus-Importer/1.0 (source-verification)"},
        )

    def close(self) -> None:
        self.client.close()

    def _get(self, url: str, params: Optional[dict[str, str]] = None) -> httpx.Response:
        if not _official_url(url):
            raise ValueError(f"Refusing non-official source URL: {url}")
        last_error: Optional[Exception] = None
        for attempt in range(self.retries):
            try:
                response = self.client.get(url, params=params)
                response.raise_for_status()
                return response
            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                last_error = exc
                if attempt + 1 < self.retries:
                    time.sleep(0.4 * (2**attempt))
        raise RuntimeError(f"Failed to fetch {url}: {last_error}")

    def discover(self, page_url: str, expected_title: str = "") -> list[SectionLink]:
        response = self._get(page_url)
        actual_title = _page_title(response.text)
        if expected_title and _title_similarity(expected_title, actual_title) < 0.65:
            raise ValueError(
                f"India Code title mismatch for {page_url}: "
                f"expected {expected_title!r}, received {actual_title!r}"
            )
        links = parse_section_links(response.text, str(response.url))
        if not links:
            raise ValueError(f"No section links discovered at {page_url}")
        return links

    def fetch_section(self, link: SectionLink) -> dict:
        response = self._get(
            f"{INDIA_CODE_ORIGIN}/SectionPageContent",
            params={"actid": link.act_id, "sectionID": link.section_id},
        )
        payload = response.json()
        text = html_to_text(str(payload.get("content") or ""))
        footnotes = html_to_text(str(payload.get("footnote") or ""))
        if len(text) < 20:
            raise ValueError(f"Section {link.section_number} returned insufficient official text")
        return {
            "section_number": link.section_number,
            "title": link.title,
            "text": text,
            "full_text": text,
            "footnotes": footnotes,
            "source_url": link.url,
            "official_source_url": link.url,
            "content_hash": _sha256(text),
        }

    def fetch_sections(self, links: Iterable[SectionLink]) -> tuple[list[dict], list[tuple[SectionLink, str]]]:
        sections: list[dict] = []
        rejected: list[tuple[SectionLink, str]] = []
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {pool.submit(self.fetch_section, link): link for link in links}
            for future in as_completed(futures):
                link = futures[future]
                try:
                    sections.append(future.result())
                except Exception as exc:  # recorded in ingestion_rejections by caller
                    rejected.append((link, str(exc)))
        order = {link.section_number: link.order for link in links}
        sections.sort(key=lambda item: (order.get(item["section_number"], 0), item["section_number"]))
        return sections, rejected


def discover_specs(
    statutes_dir: Path = STATUTES_DIR,
    domains: Optional[set[str]] = None,
    names: Optional[set[str]] = None,
) -> list[ActImportSpec]:
    specs: list[ActImportSpec] = []
    for path in sorted(statutes_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        act = data.get("act") or {}
        url = str(act.get("official_source_url") or act.get("source_url") or "")
        if "indiacode.nic.in/handle/" not in url:
            continue
        if domains and str(act.get("domain")) not in domains:
            continue
        if names and str(act.get("short_name")) not in names:
            continue
        specs.append(ActImportSpec(curated_path=path, act=act, page_url=url))
    return specs


def _merge_curated_metadata(section: dict, curated: dict, act: dict, retrieved_at: str) -> dict:
    merged = dict(section)
    official_title_tokens = set(re.findall(r"[a-z]{3,}", str(section.get("title", "")).lower()))
    curated_title_tokens = set(re.findall(r"[a-z]{3,}", str(curated.get("title", "")).lower()))
    title_union = official_title_tokens | curated_title_tokens
    title_similarity = len(official_title_tokens & curated_title_tokens) / max(1, len(title_union))
    metadata_compatible = not curated or title_similarity >= 0.30

    if metadata_compatible:
        for key in (
            "plain_language_summary",
            "subdomain",
            "keywords",
            "synonyms",
            "hindi_synonyms",
            "hinglish_synonyms",
            "historical_reference",
        ):
            if curated.get(key):
                merged[key] = curated[key]
    elif curated:
        merged["curated_metadata_conflict"] = {
            "curated_title": curated.get("title"),
            "official_title": section.get("title"),
        }
    merged.update(
        {
            "domain": curated.get("domain") or act["domain"],
            "jurisdiction": curated.get("jurisdiction") or act.get("jurisdiction", "India"),
            "state": curated.get("state") or act.get("state") or "All",
            "status": curated.get("status") or act.get("status", "CURRENT"),
            "commencement_status": curated.get("commencement_status") or act.get("commencement_status", "FULLY_COMMENCED"),
            "source_name": "India Code",
            "source_authority": act.get("source_authority") or "Government of India",
            "source_type": "Official India Code",
            "last_verified": date.today().isoformat(),
            "last_verified_at": date.today().isoformat(),
            "verification_status": "VERIFIED",
            "source_retrieved_at": retrieved_at,
        }
    )
    if not merged.get("keywords"):
        merged["keywords"] = sorted(set(re.findall(r"[A-Za-z][A-Za-z-]{3,}", merged["title"].lower())))
    merged["content_hash"] = _sha256(
        json.dumps(
            {
                "section_number": merged.get("section_number"),
                "title": merged.get("title"),
                "text": merged.get("text"),
                "footnotes": merged.get("footnotes"),
                "plain_language_summary": merged.get("plain_language_summary"),
                "domain": merged.get("domain"),
                "subdomain": merged.get("subdomain"),
                "jurisdiction": merged.get("jurisdiction"),
                "state": merged.get("state"),
                "status": merged.get("status"),
                "verification_status": merged.get("verification_status"),
                "source_url": merged.get("source_url"),
                "keywords": merged.get("keywords"),
                "synonyms": merged.get("synonyms"),
            },
            sort_keys=True,
            ensure_ascii=False,
        )
    )
    return merged


def _write_snapshot(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def _verified_fallback_sections(
    conn: sqlite3.Connection,
    spec: ActImportSpec,
    snapshot_path: Path,
    rejected: list[tuple[SectionLink, str]],
) -> list[dict]:
    """Preserve previously verified text when India Code transiently rejects a fetch.

    India Code occasionally rate-limits individual ``SectionPageContent`` calls.
    A refresh must never replace a complete official snapshot with a partial one,
    so rejected provision numbers are recovered first from the prior snapshot and
    then from the verified database row populated by an earlier successful run.
    """
    previous: dict[str, dict] = {}
    if snapshot_path.exists():
        try:
            payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
            if (payload.get("act") or {}).get("short_name") == spec.short_name:
                previous = {
                    str(item.get("section_number")): item
                    for item in payload.get("sections", [])
                    if item.get("section_number")
                }
        except (OSError, json.JSONDecodeError):
            previous = {}

    def usable(item: Optional[dict]) -> bool:
        if not item or str(item.get("verification_status", "")).upper() != "VERIFIED":
            return False
        official_url = str(item.get("official_source_url") or item.get("source_url") or "")
        return _official_url(official_url) and len(str(item.get("text") or "").strip()) >= 10

    preserved: list[dict] = []
    for link, _reason in rejected:
        section_number = str(link.section_number)
        item = previous.get(section_number)
        if not usable(item):
            row = conn.execute(
                """
                SELECT s.*
                FROM sections s
                JOIN acts a ON a.id = s.act_id
                WHERE a.short_name = ? AND s.section_number = ?
                  AND s.verification_status = 'VERIFIED'
                """,
                (spec.short_name, section_number),
            ).fetchone()
            if row:
                item = dict(row)
                item.pop("id", None)
                item.pop("act_id", None)
                for key in ("keywords", "synonyms"):
                    value = item.get(key)
                    if isinstance(value, str):
                        try:
                            item[key] = json.loads(value)
                        except json.JSONDecodeError:
                            item[key] = [value] if value else []
        if usable(item):
            preserved.append(dict(item))
    return preserved


def _record_rejection(
    conn: sqlite3.Connection,
    run_id: int,
    source_url: str,
    record_key: str,
    reason: str,
) -> None:
    conn.execute(
        """
        INSERT INTO ingestion_rejections(run_id, source_url, record_key, reason, payload_json, created_at)
        VALUES (?,?,?,?,?,?)
        """,
        (run_id, source_url, record_key, reason[:1000], "{}", _utc_now()),
    )


def ingest_official_sources(
    conn: sqlite3.Connection,
    specs: list[ActImportSpec],
    snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR,
    workers: int = 4,
    discover_only: bool = False,
) -> ImportSummary:
    summary = ImportSummary(acts_discovered=len(specs))
    started_at = _utc_now()
    cursor = conn.execute(
        "INSERT INTO ingestion_runs(source_name, started_at, status) VALUES (?,?,?)",
        ("India Code", started_at, "RUNNING"),
    )
    run_id = int(cursor.lastrowid)
    conn.commit()
    client = IndiaCodeClient(workers=workers)

    try:
        for spec in specs:
            try:
                links = client.discover(spec.page_url, expected_title=str(spec.act.get("name") or ""))
                summary.sections_discovered += len(links)
                if discover_only:
                    continue

                fetched, rejected = client.fetch_sections(links)
                summary.sections_rejected += len(rejected)
                for link, reason in rejected:
                    _record_rejection(conn, run_id, link.url, f"{spec.short_name}:{link.section_number}", reason)

                snapshot_path = snapshot_dir / f"{spec.curated_path.stem}.official.json"
                fetched.extend(_verified_fallback_sections(conn, spec, snapshot_path, rejected))

                curated_data = json.loads(spec.curated_path.read_text(encoding="utf-8"))
                curated_sections = {
                    str(item.get("section_number")): item for item in curated_data.get("sections", [])
                }
                derived_subsections = _derive_curated_subsections(fetched, curated_sections)
                fetched.extend(derived_subsections)
                summary.sections_discovered += len(derived_subsections)
                retrieved_at = _utc_now()
                sections = [
                    _merge_curated_metadata(
                        section,
                        curated_sections.get(str(section["section_number"]), {}),
                        spec.act,
                        retrieved_at,
                    )
                    for section in fetched
                ]
                act = dict(spec.act)
                act.update(
                    {
                        "source_name": "India Code",
                        "source_url": spec.page_url,
                        "official_source_url": spec.page_url,
                        "last_verified_at": date.today().isoformat(),
                        "verification_status": "VERIFIED",
                        "source_retrieved_at": retrieved_at,
                        "content_hash": _sha256("\n".join(item["content_hash"] for item in sections)),
                    }
                )
                _write_snapshot(snapshot_path, {"act": act, "sections": sections})
                result = load_file(conn, snapshot_path, force=True)
                summary.sections_inserted += result.sections_inserted
                summary.sections_updated += result.sections_updated
                summary.sections_unchanged += result.sections_skipped
                summary.sections_rejected += len(result.errors)
                for reason in result.errors:
                    _record_rejection(conn, run_id, spec.page_url, spec.short_name, reason)
            except Exception as exc:
                summary.failures += 1
                _record_rejection(conn, run_id, spec.page_url, spec.short_name, str(exc))

        status = "SUCCEEDED" if summary.failures == 0 and summary.sections_rejected == 0 else "COMPLETED_WITH_WARNINGS"
        conn.execute(
            """
            UPDATE ingestion_runs SET completed_at=?, status=?, acts_discovered=?, sections_discovered=?,
                sections_inserted=?, sections_updated=?, sections_unchanged=?, sections_rejected=?
            WHERE id=?
            """,
            (
                _utc_now(), status, summary.acts_discovered, summary.sections_discovered,
                summary.sections_inserted, summary.sections_updated, summary.sections_unchanged,
                summary.sections_rejected, run_id,
            ),
        )
        conn.commit()
        return summary
    except Exception as exc:
        conn.execute(
            "UPDATE ingestion_runs SET completed_at=?, status='FAILED', error=? WHERE id=?",
            (_utc_now(), str(exc)[:2000], run_id),
        )
        conn.commit()
        raise
    finally:
        client.close()
