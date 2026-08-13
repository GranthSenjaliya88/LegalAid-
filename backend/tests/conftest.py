"""
Pytest configuration fixture for LegalAId backend test suite.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import init_db, SessionLocal


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensure DB is initialized for tests."""
    init_db()


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """SQLAlchemy Session fixture for tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
