import sys
sys.path.insert(0, r"c:\Users\grant\Desktop\LegalAId\backend")

from app.db.database import get_connection, DB_PATH
from app.legal.corpus_search import search_corpus

print("DB Path:", DB_PATH)
conn = get_connection()
acts = conn.execute("SELECT COUNT(*) FROM acts").fetchone()[0]
sections = conn.execute("SELECT COUNT(*) FROM sections").fetchone()[0]
fts = conn.execute("SELECT COUNT(*) FROM sections_fts").fetchone()[0]
print(f"DB Records -> Acts: {acts}, Sections: {sections}, FTS: {fts}")

queries = [
    "security deposit", "unpaid wages", "cyber fraud", "defective product",
    "tenant", "salary", "rent", "consumer", "dismissal", "unauthorized transaction"
]

for q in queries:
    res = search_corpus(domain=None, facts={"incident": q})
    print(f"Query: '{q}' -> Status: {res.status}, Matches count: {len(res.matches)}")
    for m in res.matches[:2]:
        print(f"   - {m.act} Sec {m.section}: {m.title}")
