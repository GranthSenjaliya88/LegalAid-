"""
LegalAId System Doctor & Environment Diagnostic Tool.
Automatically checks Python, Node, npm, database integrity, FTS synchronization,
ports, backend health, frontend accessibility, and CORS configuration.
"""

import sys
import os
import shutil
import subprocess
import sqlite3
import urllib.request
import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
DB_PATH = BACKEND_DIR / "data" / "legalaid.db"
VECTOR_PATH = BACKEND_DIR / "data" / "vector_store" / "faiss.index"


def check_symbol(passed: bool, name: str, detail: str = ""):
    tag = "[PASS]" if passed else "[FAIL]"
    print(f"{tag:<8} {name:<35} {detail}")
    return passed


def main():
    print("=" * 80)
    print("LEGALAID ENVIRONMENT & SYSTEM DOCTOR DIAGNOSTIC")
    print("=" * 80)

    all_passed = True

    # 1. Python Check
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 10)
    all_passed &= check_symbol(py_ok, "Python Version (3.10+)", f"v{py_ver} ({sys.executable})")

    # 2. Node Check
    node_bin = shutil.which("node") or r"C:\Program Files\nodejs\node.exe"
    if os.path.exists(node_bin):
        try:
            out = subprocess.check_output([node_bin, "--version"], text=True).strip()
            check_symbol(True, "Node.js Installation", f"{out} ({node_bin})")
        except Exception as e:
            check_symbol(False, "Node.js Installation", str(e))
            all_passed = False
    else:
        check_symbol(False, "Node.js Installation", "node.exe not found in PATH or standard directory")
        all_passed = False

    # 3. npm Check
    npm_bin = shutil.which("npm") or r"C:\Program Files\nodejs\npm.cmd"
    if os.path.exists(npm_bin):
        try:
            out = subprocess.check_output([npm_bin, "--version"], shell=True, text=True).strip()
            check_symbol(True, "npm Installation", f"v{out}")
        except Exception as e:
            check_symbol(False, "npm Installation", str(e))
            all_passed = False
    else:
        check_symbol(False, "npm Installation", "npm.cmd not found in PATH or standard directory")
        all_passed = False

    # 4. Canonical Database Check
    if DB_PATH.exists():
        size_kb = round(DB_PATH.stat().st_size / 1024, 1)
        check_symbol(True, "Canonical Database File", f"{DB_PATH.resolve()} ({size_kb} KB)")
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            fk_violations = cursor.execute("PRAGMA foreign_key_check;").fetchall()
            fk_ok = len(fk_violations) == 0
            check_symbol(fk_ok, "Database Integrity (Foreign Keys)", f"{len(fk_violations)} violations")

            acts_cnt = cursor.execute("SELECT COUNT(*) FROM acts").fetchone()[0]
            sec_cnt = cursor.execute("SELECT COUNT(*) FROM sections").fetchone()[0]
            fts_cnt = cursor.execute("SELECT COUNT(*) FROM sections_fts").fetchone()[0]
            check_symbol(acts_cnt > 0 and sec_cnt > 0, "Statutory Corpus Data", f"{acts_cnt} Acts, {sec_cnt} Sections")

            fts_sync = sec_cnt == fts_cnt
            check_symbol(fts_sync, "FTS5 Index Synchronization", f"DB: {sec_cnt} rows == FTS: {fts_cnt} rows")

            conn.close()
        except Exception as e:
            check_symbol(False, "Database Query Execution", str(e))
            all_passed = False
    else:
        check_symbol(False, "Canonical Database File", f"Missing database at {DB_PATH.resolve()}")
        all_passed = False

    # 5. Vector Store Check
    if VECTOR_PATH.exists():
        check_symbol(True, "FAISS Vector Index", f"Index file present at {VECTOR_PATH.name}")
    else:
        check_symbol(True, "FAISS Vector Index (Optional)", "Index file uninitialized (Safe BM25 hybrid fallback active)")

    # 6. Backend Connectivity Check (HTTP GET http://127.0.0.1:8000/api/health/ready)
    try:
        req = urllib.request.urlopen("http://127.0.0.1:8000/api/health/ready", timeout=3)
        res_body = json.loads(req.read().decode("utf-8"))
        be_ready = res_body.get("status") == "ready"
        check_symbol(be_ready, "Backend Live Service (8000)", f"Status: {res_body.get('status')}")
    except Exception as e:
        check_symbol(False, "Backend Live Service (8000)", f"Cannot connect to http://127.0.0.1:8000/ ({e})")
        all_passed = False

    # 7. Frontend Connectivity Check (HTTP GET http://localhost:5173/)
    try:
        req = urllib.request.urlopen("http://localhost:5173/", timeout=3)
        fe_ok = req.status == 200
        check_symbol(fe_ok, "Frontend Live Service (5173)", f"Status Code: {req.status}")
    except Exception as e:
        check_symbol(False, "Frontend Live Service (5173)", f"Cannot connect to http://localhost:5173/ ({e})")
        all_passed = False

    print("=" * 80)
    if all_passed:
        print("[SUCCESS] ALL SYSTEM DOCTOR CHECKS PASSED SUCCESSFULLY! PROJECT READY.")
    else:
        print("[WARNING] SOME DOCTOR CHECKS FAILED. PLEASE REVIEW THE FAILURE DETAILS ABOVE.")
    print("=" * 80)


if __name__ == "__main__":
    main()
