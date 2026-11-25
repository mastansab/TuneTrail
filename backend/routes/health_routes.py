"""Health and monitoring routes."""

from flask import Blueprint, current_app, jsonify

from database.db import db_session

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
def health():
    db_path = current_app.config.get("DATABASE_PATH")
    try:
        with db_session(db_path) as conn:
            track_count = conn.execute("SELECT COUNT(*) FROM Tracks").fetchone()[0]
            user_count = conn.execute("SELECT COUNT(*) FROM Users").fetchone()[0]
        return jsonify({
            "status": "healthy",
            "service": "TuneTrail API",
            "database": "connected",
            "tracks": track_count,
            "users": user_count,
        }), 200
    except Exception as exc:
        return jsonify({"status": "unhealthy", "error": str(exc)}), 500
