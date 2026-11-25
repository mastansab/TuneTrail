"""Authentication, password hashing, and session/token utilities."""

from functools import wraps
from flask import current_app, g, jsonify, request, session
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import db_session


def hash_password(password: str) -> str:
    """Hash a plaintext password securely using Werkzeug."""
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against its stored hash."""
    return check_password_hash(password_hash, password)


def create_auth_token(user_id: int, secret_key: str) -> str:
    """Generate a signed URL-safe timed token for the user."""
    serializer = URLSafeTimedSerializer(secret_key, salt="tunetrail-auth")
    return serializer.dumps({"user_id": user_id})


def decode_auth_token(token: str, secret_key: str, max_age: int = 86400) -> int | None:
    """Validate and decode a signed auth token, returning user_id or None."""
    serializer = URLSafeTimedSerializer(secret_key, salt="tunetrail-auth")
    try:
        data = serializer.loads(token, max_age=max_age)
        return int(data["user_id"])
    except (BadSignature, SignatureExpired, KeyError, ValueError):
        return None


def get_request_user_id() -> int | None:
    """Extract authenticated user_id from Bearer token or Flask session."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        uid = decode_auth_token(
            token,
            current_app.config["SECRET_KEY"],
            current_app.config.get("TOKEN_EXPIRY_SECONDS", 86400),
        )
        if uid is not None:
            return uid
    sess_uid = session.get("user_id")
    return int(sess_uid) if sess_uid is not None else None


def require_auth(fn):
    """Decorator enforcing valid user authentication."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_request_user_id()
        if user_id is None:
            return jsonify({"error": "Authentication required"}), 401

        db_path = current_app.config.get("DATABASE_PATH")
        with db_session(db_path) as conn:
            user = conn.execute(
                "SELECT id, username, email, display_name, role, created_at FROM Users WHERE id = ?",
                (user_id,),
            ).fetchone()
        if user is None:
            return jsonify({"error": "Invalid or expired session"}), 401

        g.current_user = dict(user)
        return fn(*args, **kwargs)

    return wrapper
