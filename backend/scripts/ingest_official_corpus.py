"""CLI for expanding the local corpus from official India Code pages."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.database import get_connection, init_db  # noqa: E402
from corpus.loader import STATUTES_DIR, load_all  # noqa: E402
from corpus.official_importer import (  # noqa: E402
    DEFAULT_SNAPSHOT_DIR,
    discover_specs,
    ingest_official_sources,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import complete, source-linked statutory sections from India Code."
    )
    parser.add_argument("--domain", action="append", help="Only import this domain; may be repeated.")
    parser.add_argument("--act", action="append", help="Only import this exact short name; may be repeated.")
    parser.add_argument("--limit-acts", type=int, default=0, help="Limit the number of acts (0 = all).")
    parser.add_argument("--workers", type=int, default=4, choices=range(1, 9))
    parser.add_argument("--discover-only", action="store_true", help="Count provisions without downloading text.")
    parser.add_argument("--snapshot-dir", type=Path, default=DEFAULT_SNAPSHOT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    init_db()
    conn = get_connection()
    try:
        if conn.execute("SELECT COUNT(*) FROM acts").fetchone()[0] == 0:
            load_all(conn, statutes_dir=STATUTES_DIR)

        specs = discover_specs(
            domains=set(args.domain or []),
            names=set(args.act or []),
        )
        if args.limit_acts > 0:
            specs = specs[: args.limit_acts]
        if not specs:
            print("No matching India Code sources were found in the curated statute manifests.")
            return 2

        summary = ingest_official_sources(
            conn,
            specs,
            snapshot_dir=args.snapshot_dir,
            workers=args.workers,
            discover_only=args.discover_only,
        )
        print(json.dumps(summary.__dict__, indent=2))
        return 0 if summary.failures == 0 else 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
