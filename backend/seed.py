"""
seed.py — Admin CLI: load all statute JSON files into the database.

Usage:
    python seed.py              # insert new sections, skip existing
    python seed.py --force      # also update existing sections

This is the ONLY place that writes statute data to the database.
The LLM has no access to this script's write path.
"""

import sys
import argparse
import io

# Force UTF-8 output so Unicode characters don't crash on Windows cp1252 consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

# Make backend root importable
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db, get_connection
from corpus.loader import load_all, STATUTES_DIR
from corpus.verify import run_verify


def main():
    parser = argparse.ArgumentParser(description="Seed LegalAId corpus database")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Update existing sections (default: skip duplicates)",
    )
    parser.add_argument(
        "--dir",
        default=str(STATUTES_DIR),
        help="Path to directory containing statute JSON files",
    )
    args = parser.parse_args()

    statutes_dir = Path(args.dir)
    if not statutes_dir.is_dir():
        print(f"ERROR: statutes directory not found: {statutes_dir}")
        sys.exit(1)

    print("=" * 60, flush=True)
    print("LegalAId Corpus Seeder")
    print("=" * 60, flush=True)
    print(f"Statutes dir : {statutes_dir}")
    print(f"Force update : {args.force}")
    print()

    # Initialise schema
    init_db()
    conn = get_connection()

    # Load all statute files
    results = load_all(conn, statutes_dir=statutes_dir, force=args.force)

    # Sync historical status across sections
    conn.execute("""
        UPDATE sections
        SET status = 'HISTORICAL', repealed = 1
        WHERE act_id IN (SELECT id FROM acts WHERE UPPER(status) IN ('HISTORICAL', 'REPEALED'))
    """)
    conn.commit()

    # Summary
    print()
    print("-" * 60)
    total_inserted = sum(r.sections_inserted for r in results)
    total_updated  = sum(r.sections_updated  for r in results)
    total_skipped  = sum(r.sections_skipped  for r in results)
    total_errors   = sum(len(r.errors) for r in results)
    print(f"Acts processed : {len(results)}")
    print(f"Sections inserted : {total_inserted}")
    print(f"Sections updated  : {total_updated}")
    print(f"Sections skipped  : {total_skipped}")
    print(f"Warnings/errors   : {total_errors}")
    print()

    # Run integrity checks
    print("Running corpus integrity checks …")
    report = run_verify(conn)
    print(f"Result: {report.summary}")
    for issue in report.issues:
        tag = "ERROR  " if issue.severity == "error" else "WARNING"
        print(f"  [{tag}] [{issue.check}] {issue.detail}")

    conn.close()

    if not report.passed:
        print("\nSeeding completed with errors. Fix issues before running the API.")
        sys.exit(1)

    print("\nSeeding complete. Corpus is clean and ready.")
    sys.exit(0)


if __name__ == "__main__":
    main()
