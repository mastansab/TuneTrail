"""Listening history routes."""

from flask import Blueprint, current_app, g, jsonify, request

from backend.services.music_service import get_listening_history, record_listening_event
from backend.utils.auth import require_auth

history_bp = Blueprint("history", __name__, url_prefix="/api/history")


@history_bp.get("")
@require_auth
def list_history():
    limit = min(100, max(1, int(request.args.get("limit", 30))))
    items = get_listening_history(current_app.config.get("DATABASE_PATH"), g.current_user["id"], limit=limit)
    return jsonify({"history": items, "total": len(items)}), 200


@history_bp.post("")
@require_auth
def add_history():
    data = request.get_json(silent=True) or {}
    track_id = data.get("track_id")
    if track_id is None:
        return jsonify({"error": "track_id is required"}), 400
    payload, status = record_listening_event(
        db_path=current_app.config.get("DATABASE_PATH"),
        user_id=g.current_user["id"],
        track_id=int(track_id),
        play_duration_sec=int(data.get("play_duration_sec", 180)),
        completed=bool(data.get("completed", True)),
    )
    return jsonify(payload), status
