"""Playlist CRUD and track management routes."""

from flask import Blueprint, current_app, g, jsonify, request

from backend.services.music_service import (
    add_track_to_playlist,
    create_playlist,
    delete_playlist,
    get_playlists,
    remove_track_from_playlist,
)
from backend.utils.auth import require_auth

playlists_bp = Blueprint("playlists", __name__, url_prefix="/api/playlists")


@playlists_bp.get("")
@require_auth
def list_playlists():
    playlists = get_playlists(current_app.config.get("DATABASE_PATH"), g.current_user["id"])
    return jsonify({"playlists": playlists, "total": len(playlists)}), 200


@playlists_bp.post("")
@require_auth
def new_playlist():
    data = request.get_json(silent=True) or {}
    payload, status = create_playlist(
        current_app.config.get("DATABASE_PATH"),
        g.current_user["id"],
        name=data.get("name", ""),
        description=data.get("description", ""),
    )
    return jsonify(payload), status


@playlists_bp.delete("/<int:playlist_id>")
@require_auth
def remove_playlist(playlist_id: int):
    payload, status = delete_playlist(
        current_app.config.get("DATABASE_PATH"), g.current_user["id"], playlist_id
    )
    return jsonify(payload), status


@playlists_bp.post("/<int:playlist_id>/tracks")
@require_auth
def add_track(playlist_id: int):
    data = request.get_json(silent=True) or {}
    track_id = data.get("track_id")
    if track_id is None:
        return jsonify({"error": "track_id is required"}), 400
    payload, status = add_track_to_playlist(
        current_app.config.get("DATABASE_PATH"), g.current_user["id"], playlist_id, int(track_id)
    )
    return jsonify(payload), status


@playlists_bp.delete("/<int:playlist_id>/tracks/<int:track_id>")
@require_auth
def remove_track(playlist_id: int, track_id: int):
    payload, status = remove_track_from_playlist(
        current_app.config.get("DATABASE_PATH"), g.current_user["id"], playlist_id, track_id
    )
    return jsonify(payload), status
