"""User authentication, profile, and preference management service."""

import json
import sqlite3
from pathlib import Path

from backend.utils.auth import create_auth_token, hash_password, verify_password
from database.db import db_session


def register_user(
    db_path: str | Path | None,
    secret_key: str,
    username: str,
    email: str,
    password: str,
    display_name: str | None = None,
    preferred_genres: list[str] | None = None,
    preferred_artists: list[str] | None = None,
) -> tuple[dict, int]:
    """Register a new user with hashed password and default preferences."""
    username = (username or "").strip()
    email = (email or "").strip().lower()
    display_name = (display_name or username).strip()

    if len(username) < 3:
        return {"error": "Username must be at least 3 characters"}, 400
    if "@" not in email or "." not in email.split("@")[-1]:
        return {"error": "Valid email address is required"}, 400
    if len(password or "") < 6:
        return {"error": "Password must be at least 6 characters"}, 400

    pw_hash = hash_password(password)
    try:
        with db_session(db_path) as conn:
            cur = conn.execute(
                """
                INSERT INTO Users (username, email, password_hash, display_name)
                VALUES (?, ?, ?, ?)
                """,
                (username, email, pw_hash, display_name),
            )
            user_id = cur.lastrowid
            conn.execute(
                """
                INSERT INTO UserPreferences (user_id, preferred_genres, preferred_artists, hybrid_alpha, avoid_recent_count)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    json.dumps(preferred_genres or []),
                    json.dumps(preferred_artists or []),
                    0.6,
                    5,
                ),
            )
            user = dict(
                conn.execute(
                    "SELECT id, username, email, display_name, role, created_at FROM Users WHERE id = ?",
                    (user_id,),
                ).fetchone()
            )
    except sqlite3.IntegrityError:
        return {"error": "Username or email already exists"}, 409

    token = create_auth_token(user["id"], secret_key)
    return {"user": user, "token": token}, 201


def login_user(
    db_path: str | Path | None,
    secret_key: str,
    identifier: str,
    password: str,
) -> tuple[dict, int]:
    """Authenticate a user by username or email and return user + signed token."""
    identifier = (identifier or "").strip()
    if not identifier or not password:
        return {"error": "Username/email and password are required"}, 400

    with db_session(db_path) as conn:
        row = conn.execute(
            """
            SELECT id, username, email, password_hash, display_name, role, created_at
            FROM Users
            WHERE lower(username) = lower(?) OR lower(email) = lower(?)
            """,
            (identifier, identifier),
        ).fetchone()

    if row is None or not verify_password(password, row["password_hash"]):
        return {"error": "Invalid credentials"}, 401

    user = {
        "id": row["id"],
        "username": row["username"],
        "email": row["email"],
        "display_name": row["display_name"],
        "role": row["role"],
        "created_at": str(row["created_at"]),
    }
    token = create_auth_token(user["id"], secret_key)
    return {"user": user, "token": token}, 200


def get_preferences(db_path: str | Path | None, user_id: int) -> dict:
    """Fetch user preferences or return sensible defaults."""
    with db_session(db_path) as conn:
        row = conn.execute(
            """
            SELECT preferred_genres, preferred_artists, hybrid_alpha, avoid_recent_count, updated_at
            FROM UserPreferences WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    if row is None:
        return {
            "preferred_genres": [],
            "preferred_artists": [],
            "hybrid_alpha": 0.6,
            "avoid_recent_count": 5,
        }
    return {
        "preferred_genres": json.loads(row["preferred_genres"]),
        "preferred_artists": json.loads(row["preferred_artists"]),
        "hybrid_alpha": float(row["hybrid_alpha"]),
        "avoid_recent_count": int(row["avoid_recent_count"]),
        "updated_at": str(row["updated_at"]),
    }


def update_profile_and_preferences(
    db_path: str | Path | None,
    user_id: int,
    display_name: str | None = None,
    preferred_genres: list[str] | None = None,
    preferred_artists: list[str] | None = None,
    hybrid_alpha: float | None = None,
    avoid_recent_count: int | None = None,
) -> tuple[dict, int]:
    """Update user display name and recommendation preferences."""
    current_prefs = get_preferences(db_path, user_id)
    new_genres = preferred_genres if preferred_genres is not None else current_prefs["preferred_genres"]
    new_artists = preferred_artists if preferred_artists is not None else current_prefs["preferred_artists"]
    new_alpha = float(hybrid_alpha) if hybrid_alpha is not None else current_prefs["hybrid_alpha"]
    new_avoid = int(avoid_recent_count) if avoid_recent_count is not None else current_prefs["avoid_recent_count"]

    if not (0.0 <= new_alpha <= 1.0):
        return {"error": "hybrid_alpha must be between 0.0 and 1.0"}, 400
    if new_avoid < 0:
        return {"error": "avoid_recent_count must be >= 0"}, 400

    with db_session(db_path) as conn:
        if display_name is not None and display_name.strip():
            conn.execute(
                "UPDATE Users SET display_name = ? WHERE id = ?",
                (display_name.strip(), user_id),
            )
        conn.execute(
            """
            INSERT INTO UserPreferences (user_id, preferred_genres, preferred_artists, hybrid_alpha, avoid_recent_count, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                preferred_genres = excluded.preferred_genres,
                preferred_artists = excluded.preferred_artists,
                hybrid_alpha = excluded.hybrid_alpha,
                avoid_recent_count = excluded.avoid_recent_count,
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, json.dumps(new_genres), json.dumps(new_artists), new_alpha, new_avoid),
        )
        user = dict(
            conn.execute(
                "SELECT id, username, email, display_name, role, created_at FROM Users WHERE id = ?",
                (user_id,),
            ).fetchone()
        )
    return {"user": user, "preferences": get_preferences(db_path, user_id)}, 200
