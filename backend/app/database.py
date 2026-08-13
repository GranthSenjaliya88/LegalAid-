"""
app/database.py — Backward-compatibility proxy module.
All database connections and initialization now route through app.db.database.
"""

from app.db.database import DB_PATH, get_connection, init_db, get_db

__all__ = ["DB_PATH", "get_connection", "init_db", "get_db"]

