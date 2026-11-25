"""Favourites management routes."""

from flask import Blueprint, current_app, g, jsonify, request

from backend.services.music_service import add_favourite, get_favourites, remove_favourite
from backend.utils.auth import require_auth

favourites_bp = Blueprint("favourites", __name__, url_prefix="/api/favourites")


@favourites_bp.get("")
@require_auth
def list_favs():
    favs = get_favourites(current_app.config.get("DATABASE_PATH"), g.current_user["id"])
    return jsonify({"favourites": favs, "total": len(favs)}), 200


@favourites_bp.post("")
@require_auth
def create_fav():
    data = request.get_json(silent=True) or {}
    track_id = data.get("track_id")
    if track_id is None:
        return jsonify({"error": "track_id is required"}), 400
    payload, status = add_favourite(
        current_app.config.get("DATABASE_PATH"), g.current_user["id"], int(track_id)
    )
    return jsonify(payload), status


@favourites_bp.delete("/<int:track_id>")
@require_auth
def delete_fav(track_id: int):
    payload, status = remove_favourite(
        current_app.config.get("DATABASE_PATH"), g.current_user["id"], track_id
    )
    return jsonify(payload), status
