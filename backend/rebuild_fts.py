"""
rebuild_fts.py — Drop and rebuild the FTS5 index from the sections table.

Run this whenever the FTS index drifts out of sync with `sections`
(e.g. after a re-seed that duplicated FTS rows, or after changing the
sections_fts schema).

Design notes:
- sections_fts is a *contentless* FTS5 table (content=''). On common SQLite
  builds a plain `DELETE FROM sections_fts` is rejected, so this script fully
  drops and recreates the virtual table and its triggers.
- Every FTS row is inserted with an explicit `rowid = sections.id` so the index
  stays 1:1 with `sections`. Retrieval joins `sections s ON s.id = fts.rowid`,
  so this mapping is load-bearing.
- Uses the stdlib `sqlite3` driver directly (no app/ORM imports) so it runs in
  any environment, including CI.

Usage:
    python rebuild_fts.py [path/to/legalaid.db]
"""
import os
import re
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path(__file__).parent / "data" / "legalaid.db"

# Columns written to the FTS index (after the implicit rowid). Kept identical to
# the trigger/DDL definitions in app/db/database.py.
FTS_COLS = (
    "section_id", "act_short_name", "section_number", "title", "full_text",
    "domain", "subdomain", "state", "keywords", "synonyms",
    "historical_reference", "status",
)

FTS_CREATE = """
CREATE VIRTUAL TABLE sections_fts USING fts5(
    section_id   UNINDEXED,
    act_short_name,
    section_number,
    title,
    full_text,
    domain,
    subdomain,
    state,
    keywords,
    synonyms,
    historical_reference,
    status,
    content      = '',
    tokenize     = 'unicode61'
);
"""

TRIGGERS = """
CREATE TRIGGER sections_ai AFTER INSERT ON sections BEGIN
    INSERT INTO sections_fts(rowid, section_id, act_short_name, section_number, title, full_text, domain, subdomain, state, keywords, synonyms, historical_reference, status)
    SELECT new.id, new.id, a.short_name, new.section_number, COALESCE(new.title,''), new.text,
           new.domain, COALESCE(new.subdomain,''), COALESCE(new.state,'All'),
           COALESCE(new.keywords,'[]'), COALESCE(new.synonyms,'[]'),
           COALESCE(new.historical_reference,''), COALESCE(new.status,'CURRENT')
    FROM   acts a WHERE a.id = new.act_id;
END;

CREATE TRIGGER sections_ad AFTER DELETE ON sections BEGIN
    INSERT INTO sections_fts(sections_fts, rowid, section_id, act_short_name, section_number, title, full_text, domain, subdomain, state, keywords, synonyms, historical_reference, status)
    SELECT 'delete', old.id, old.id, a.short_name, old.section_number, COALESCE(old.title,''), old.text,
           old.domain, COALESCE(old.subdomain,''), COALESCE(old.state,'All'),
           COALESCE(old.keywords,'[]'), COALESCE(old.synonyms,'[]'),
           COALESCE(old.historical_reference,''), COALESCE(old.status,'CURRENT')
    FROM   acts a WHERE a.id = old.act_id;
END;

CREATE TRIGGER sections_au AFTER UPDATE ON sections BEGIN
    INSERT INTO sections_fts(sections_fts, rowid, section_id, act_short_name, section_number, title, full_text, domain, subdomain, state, keywords, synonyms, historical_reference, status)
    SELECT 'delete', old.id, old.id, a.short_name, old.section_number, COALESCE(old.title,''), old.text,
           old.domain, COALESCE(old.subdomain,''), COALESCE(old.state,'All'),
           COALESCE(old.keywords,'[]'), COALESCE(old.synonyms,'[]'),
           COALESCE(old.historical_reference,''), COALESCE(old.status,'CURRENT')
    FROM   acts a WHERE a.id = old.act_id;
    INSERT INTO sections_fts(rowid, section_id, act_short_name, section_number, title, full_text, domain, subdomain, state, keywords, synonyms, historical_reference, status)
    SELECT new.id, new.id, a.short_name, new.section_number, COALESCE(new.title,''), new.text,
           new.domain, COALESCE(new.subdomain,''), COALESCE(new.state,'All'),
           COALESCE(new.keywords,'[]'), COALESCE(new.synonyms,'[]'),
           COALESCE(new.historical_reference,''), COALESCE(new.status,'CURRENT')
    FROM   acts a WHERE a.id = new.act_id;
END;
"""

# Selects rowid (= s.id) followed by the 12 FTS_COLS values, in order.
BULK_SELECT = """
    SELECT s.id, s.id, a.short_name, s.section_number, COALESCE(s.title,''), s.text,
           s.domain, COALESCE(s.subdomain,''), COALESCE(s.state,'All'),
           COALESCE(s.keywords,'[]'), COALESCE(s.synonyms,'[]'),
           COALESCE(s.historical_reference,''), COALESCE(s.status,'CURRENT')
    FROM   sections s
    JOIN   acts a ON a.id = s.act_id
    WHERE  s.is_active = 1
"""


def _resolve_db_path() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    m = re.match(r"sqlite:///(.*)", os.environ.get("DATABASE_URL", ""))
    return Path(m.group(1)) if m else DEFAULT_DB


def rebuild_fts(db_path: Path) -> int:
    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}")

    conn = sqlite3.connect(str(db_path))
    try:
        before = conn.execute("SELECT COUNT(*) FROM sections_fts").fetchone()[0]
        active = conn.execute("SELECT COUNT(*) FROM sections WHERE is_active = 1").fetchone()[0]
        print(f"Before: sections_fts={before}, active sections={active}")

        conn.executescript(
            "DROP TRIGGER IF EXISTS sections_ai;"
            "DROP TRIGGER IF EXISTS sections_ad;"
            "DROP TRIGGER IF EXISTS sections_au;"
            "DROP TABLE IF EXISTS sections_fts;"
        )
        conn.executescript(FTS_CREATE)

        rows = conn.execute(BULK_SELECT).fetchall()
        placeholders = ",".join(["?"] * (1 + len(FTS_COLS)))  # rowid + 12 cols
        conn.executemany(
            f"INSERT INTO sections_fts(rowid, {', '.join(FTS_COLS)}) VALUES ({placeholders})",
            rows,
        )
        conn.executescript(TRIGGERS)
        conn.commit()

        after = conn.execute("SELECT COUNT(*) FROM sections_fts").fetchone()[0]
        distinct = conn.execute("SELECT COUNT(DISTINCT rowid) FROM sections_fts").fetchone()[0]
        orphans = conn.execute(
            "SELECT COUNT(*) FROM sections_fts f "
            "LEFT JOIN sections s ON s.id = f.rowid WHERE s.id IS NULL"
        ).fetchone()[0]
        test = conn.execute("SELECT COUNT(*) FROM sections_fts WHERE sections_fts MATCH 'the'").fetchone()[0]
        print(f"After:  sections_fts={after} (distinct rowid={distinct})")
        print(f"Orphan FTS rows (no matching section): {orphans}")
        print(f"Test MATCH 'the' returned {test} rows")

        if after != active:
            raise SystemExit(f"FAIL: FTS row count {after} != active sections {active}")
        if orphans != 0:
            raise SystemExit(f"FAIL: {orphans} orphan FTS rows remain")
        print("FTS rebuild complete and verified.")
        return after
    finally:
        conn.close()


if __name__ == "__main__":
    rebuild_fts(_resolve_db_path())
