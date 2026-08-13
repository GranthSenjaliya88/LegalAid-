"""
LegalAId — Database initialization and session management.
Uses SQLAlchemy ORM with SQLite (WAL mode + FTS5) as fallback,
and supports switching to PostgreSQL via DATABASE_URL.
"""

import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.db.models import Base

# DB Path default for SQLite fallback
DB_PATH = Path(__file__).parent.parent.parent / "data" / "legalaid.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

db_url = settings.DATABASE_URL
if db_url.startswith("sqlite") and "///" in db_url:
    rel_path = db_url.split("///")[-1]
    abs_path = (Path(__file__).parent.parent.parent / rel_path).resolve()
    db_url = f"sqlite:///{abs_path}"

connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    echo=False,
    future=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


FTS_DDL = """
-- FTS5 Virtual table mirroring sections for BM25 full-text search
CREATE VIRTUAL TABLE IF NOT EXISTS sections_fts USING fts5(
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

-- Triggers to keep FTS index synchronized with sections table.
-- IMPORTANT: sections_fts is a *contentless* FTS5 table (content=''). On this
-- SQLite build a plain `DELETE FROM sections_fts` is rejected ("cannot DELETE
-- from contentless fts5 table"), so deletes/updates MUST use the special
-- 'delete' command with the originally-indexed column values. Inserts pin
-- rowid = sections.id so the index stays 1:1 with sections and re-seeds
-- replace rather than append (this was the cause of duplicate FTS rows).
CREATE TRIGGER IF NOT EXISTS sections_ai AFTER INSERT ON sections BEGIN
    INSERT INTO sections_fts(rowid, section_id, act_short_name, section_number, title, full_text, domain, subdomain, state, keywords, synonyms, historical_reference, status)
    SELECT new.id, new.id,
           a.short_name,
           new.section_number,
           COALESCE(new.title, ''),
           new.text,
           new.domain,
           COALESCE(new.subdomain, ''),
           COALESCE(new.state, 'All'),
           COALESCE(new.keywords, '[]'),
           COALESCE(new.synonyms, '[]'),
           COALESCE(new.historical_reference, ''),
           COALESCE(new.status, 'CURRENT')
    FROM   acts a WHERE a.id = new.act_id;
END;

CREATE TRIGGER IF NOT EXISTS sections_ad AFTER DELETE ON sections BEGIN
    INSERT INTO sections_fts(sections_fts, rowid, section_id, act_short_name, section_number, title, full_text, domain, subdomain, state, keywords, synonyms, historical_reference, status)
    SELECT 'delete', old.id, old.id,
           a.short_name,
           old.section_number,
           COALESCE(old.title, ''),
           old.text,
           old.domain,
           COALESCE(old.subdomain, ''),
           COALESCE(old.state, 'All'),
           COALESCE(old.keywords, '[]'),
           COALESCE(old.synonyms, '[]'),
           COALESCE(old.historical_reference, ''),
           COALESCE(old.status, 'CURRENT')
    FROM   acts a WHERE a.id = old.act_id;
END;

CREATE TRIGGER IF NOT EXISTS sections_au AFTER UPDATE ON sections BEGIN
    INSERT INTO sections_fts(sections_fts, rowid, section_id, act_short_name, section_number, title, full_text, domain, subdomain, state, keywords, synonyms, historical_reference, status)
    SELECT 'delete', old.id, old.id,
           a.short_name,
           old.section_number,
           COALESCE(old.title, ''),
           old.text,
           old.domain,
           COALESCE(old.subdomain, ''),
           COALESCE(old.state, 'All'),
           COALESCE(old.keywords, '[]'),
           COALESCE(old.synonyms, '[]'),
           COALESCE(old.historical_reference, ''),
           COALESCE(old.status, 'CURRENT')
    FROM   acts a WHERE a.id = old.act_id;
    INSERT INTO sections_fts(rowid, section_id, act_short_name, section_number, title, full_text, domain, subdomain, state, keywords, synonyms, historical_reference, status)
    SELECT new.id, new.id,
           a.short_name,
           new.section_number,
           COALESCE(new.title, ''),
           new.text,
           new.domain,
           COALESCE(new.subdomain, ''),
           COALESCE(new.state, 'All'),
           COALESCE(new.keywords, '[]'),
           COALESCE(new.synonyms, '[]'),
           COALESCE(new.historical_reference, ''),
           COALESCE(new.status, 'CURRENT')
    FROM   acts a WHERE a.id = new.act_id;
END;
"""


def _apply_migrations(raw_conn: sqlite3.Connection) -> None:
    """Safely apply column migrations to existing SQLite tables if missing."""
    def get_cols(table_name: str) -> set:
        try:
            return {row[1] for row in raw_conn.execute(f"PRAGMA table_info({table_name})").fetchall()}
        except Exception:
            return set()

    acts_cols = get_cols("acts")
    sections_cols = get_cols("sections")
    facts_cols = get_cols("case_facts")
    rules_cols = get_cols("rules")
    regulations_cols = get_cols("regulations")
    notifications_cols = get_cols("notifications")
    judgments_cols = get_cols("judgments")
    authorities_cols = get_cols("authorities")
    procedures_cols = get_cols("procedures")
    sources_cols = get_cols("sources")

    acts_new = [
        ("long_name", "TEXT"),
        ("long_title", "TEXT"),
        ("jurisdiction", "VARCHAR(100) DEFAULT 'INDIA'"),
        ("state", "VARCHAR(100)"),
        ("city", "VARCHAR(100)"),
        ("effective_from", "VARCHAR(20)"),
        ("effective_to", "VARCHAR(20)"),
        ("commencement_status", "VARCHAR(30) DEFAULT 'UNKNOWN'"),
        ("official_source_url", "VARCHAR(500)"),
        ("source_authority", "VARCHAR(255)"),
        ("enforcement_date", "VARCHAR(20)"),
        ("status", "VARCHAR(30) DEFAULT 'CURRENT'"),
        ("repealed_by", "VARCHAR(255)"),
        ("supersedes", "VARCHAR(255)"),
        ("superseded_by", "VARCHAR(255)"),
        ("last_verified_at", "VARCHAR(20)"),
        ("verification_status", "VARCHAR(30) DEFAULT 'VERIFIED'"),
        ("source_id", "INTEGER"),
    ]
    for col_name, col_type in acts_new:
        if col_name not in acts_cols:
            raw_conn.execute(f"ALTER TABLE acts ADD COLUMN {col_name} {col_type};")

    sections_new = [
        ("full_text", "TEXT"),
        ("chapter", "VARCHAR(100)"),
        ("subsection", "VARCHAR(50)"),
        ("clause", "VARCHAR(50)"),
        ("synonyms", "TEXT DEFAULT '[]'"),
        ("hindi_synonyms", "TEXT DEFAULT '[]'"),
        ("hinglish_synonyms", "TEXT DEFAULT '[]'"),
        ("city", "VARCHAR(100)"),
        ("effective_to", "VARCHAR(20)"),
        ("enforcement_date", "VARCHAR(20)"),
        ("commencement_status", "VARCHAR(30) DEFAULT 'FULLY_COMMENCED'"),
        ("repealed", "BOOLEAN DEFAULT 0"),
        ("repealed_by", "VARCHAR(255)"),
        ("supersedes", "VARCHAR(255)"),
        ("superseded_by", "VARCHAR(255)"),
        ("historical_reference", "VARCHAR(255)"),
        ("official_source_url", "VARCHAR(500)"),
        ("source_type", "VARCHAR(100)"),
        ("source_authority", "VARCHAR(255)"),
        ("last_verified_at", "VARCHAR(20)"),
        ("verification_status", "VARCHAR(30) DEFAULT 'VERIFIED'"),
        ("source_id", "INTEGER"),
        ("dataset_name", "VARCHAR(100)"),
        ("dataset_record_id", "VARCHAR(100)"),
        ("license", "VARCHAR(100)"),
        ("usage_type", "VARCHAR(50)"),
    ]
    for col_name, col_type in sections_new:
        if col_name not in sections_cols:
            raw_conn.execute(f"ALTER TABLE sections ADD COLUMN {col_name} {col_type};")

    if "text" in sections_cols and "full_text" in sections_cols:
        raw_conn.execute("UPDATE sections SET full_text = text WHERE (full_text IS NULL OR full_text = '') AND text IS NOT NULL;")

    facts_new = [
        ("subdomain", "VARCHAR(100)"),
        ("city", "VARCHAR(100)"),
        ("district", "VARCHAR(100)"),
        ("incident_date", "VARCHAR(100)"),
        ("notice_sent", "BOOLEAN"),
    ]
    for col_name, col_type in facts_new:
        if col_name not in facts_cols:
            raw_conn.execute(f"ALTER TABLE case_facts ADD COLUMN {col_name} {col_type};")

    for table_name, cols_set, new_cols in [
        ("rules", rules_cols, [("source_id", "INTEGER"), ("relevant_act", "VARCHAR(255)")]),
        ("regulations", regulations_cols, [("source_id", "INTEGER"), ("relevant_act", "VARCHAR(255)")]),
        ("notifications", notifications_cols, [("source_id", "INTEGER"), ("subject", "VARCHAR(500)"), ("summary", "TEXT"), ("applicable_to", "TEXT")]),
        ("judgments", judgments_cols, [("source_id", "INTEGER"), ("binding_level", "VARCHAR(50) DEFAULT 'PERSUASIVE'"), ("facts", "TEXT"), ("issues", "TEXT"), ("decision", "TEXT"), ("legal_principles", "TEXT"), ("legal_provisions", "TEXT")]),
        ("authorities", authorities_cols, [("source_id", "INTEGER")]),
        ("procedures", procedures_cols, [("source_id", "INTEGER")]),
        ("sources", sources_cols, [("official_url", "VARCHAR(500)"), ("version", "VARCHAR(20) DEFAULT '1.0'"), ("last_verified_at", "VARCHAR(50)")]),
    ]:
        if cols_set:
            for col_name, col_type in new_cols:
                if col_name not in cols_set:
                    raw_conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type};")

    raw_conn.commit()


def init_db() -> None:
    """Initialize database tables and triggers."""
    Base.metadata.create_all(bind=engine)

    if engine.name == "sqlite":
        with engine.connect() as conn:
            raw_conn = conn.connection
            _apply_migrations(raw_conn)
            raw_conn.executescript(FTS_DDL)
            raw_conn.commit()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def configure_sqlite(db):
    db.execute(text("PRAGMA journal_mode=WAL;"))
    db.execute(text("PRAGMA foreign_keys=ON;"))


def get_connection() -> sqlite3.Connection:
    raw_path = str(DB_PATH)
    conn = sqlite3.connect(raw_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

