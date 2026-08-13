from app.db.database import get_connection
from corpus.verify import run_verify

conn = get_connection()
report = run_verify(conn)
print("passed:", report.passed)
for i in report.issues:
    print("Issue:", i.check, i.severity, i.detail)
conn.close()
