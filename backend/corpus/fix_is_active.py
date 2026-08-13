import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "legalaid.db"
conn = sqlite3.connect(DB_PATH)
conn.execute("UPDATE sections SET is_active=1 WHERE is_active IS NULL OR is_active=0;")
conn.commit()

total = conn.execute("SELECT COUNT(*) FROM sections").fetchone()[0]
active = conn.execute("SELECT COUNT(*) FROM sections WHERE is_active=1").fetchone()[0]
fts = conn.execute("SELECT COUNT(*) FROM sections_fts").fetchone()[0]
conn.close()

print(f"Total Sections: {total} | Active Sections: {active} | FTS Rows: {fts}")
