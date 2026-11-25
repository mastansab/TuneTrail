"""Unit tests for authentication utilities and SQLite database integrity."""

import sqlite3
import pytest

from backend.utils.auth import create_auth_token, decode_auth_token, hash_password, verify_password
from database.db import db_session
from database.seed import seed_database


def test_password_hashing_and_verification():
    pw_hash = hash_password("SecurePass@2026")
    assert pw_hash != "SecurePass@2026"
    assert verify_password("SecurePass@2026", pw_hash) is True
    assert verify_password("WrongPassword", pw_hash) is False


def test_token_roundtrip_and_tamper_rejection():
    secret = "unit-test-secret"
    token = create_auth_token(42, secret)
    assert decode_auth_token(token, secret) == 42
    assert decode_auth_token(token + "tamper", secret) is None
    assert decode_auth_token(token, "different-secret") is None


def test_seed_idempotency_and_counts(test_db):
    res_again = seed_database(test_db, force=False)
    assert res_again["status"] == "already_seeded"
    assert res_again["tracks"] == 60

    with db_session(test_db) as conn:
        user_count = conn.execute("SELECT COUNT(*) FROM Users").fetchone()[0]
        hist_count = conn.execute("SELECT COUNT(*) FROM ListeningHistory").fetchone()[0]
        assert user_count == 13
        assert hist_count == 123


def test_foreign_key_constraint_enforced(test_db):
    with pytest.raises(sqlite3.IntegrityError):
        with db_session(test_db) as conn:
            conn.execute(
                "INSERT INTO Playlists (user_id, name) VALUES (?, ?)",
                (999999, "Orphan Playlist"),
            )
