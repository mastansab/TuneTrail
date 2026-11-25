"""Shared pytest fixtures for TuneTrail unit, integration, and E2E tests."""

import pytest

from backend.app import create_app
from database.seed import seed_database


@pytest.fixture()
def test_db(tmp_path):
    """Create a fresh seeded SQLite database in a temporary directory."""
    db_file = tmp_path / "test_tunetrail.db"
    seed_database(db_file, force=True)
    return db_file


@pytest.fixture()
def app(test_db):
    """Create a Flask test application bound to the temporary database."""
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DATABASE_PATH": str(test_db),
        }
    )
    return application


@pytest.fixture()
def client(app):
    """Return a Flask test client."""
    return app.test_client()
