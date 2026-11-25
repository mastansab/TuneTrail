"""Music catalog routes."""

from flask import Blueprint, current_app, jsonify, request

from backend.services.music_service import get_catalog_metadata, list_tracks
from backend.utils.auth import get_request_user_id

tracks_bp = Blueprint("tracks", __name__, url_prefix="/api/tracks")


@tracks_bp.get("")
def get_tracks():
    user_id = get_request_user_id()
    tracks = list_tracks(
        db_path=current_app.config.get("DATABASE_PATH"),
        user_id=user_id,
        query=request.args.get("q", ""),
        genre=request.args.get("genre", ""),
        artist=request.args.get("artist", ""),
        sort_by=request.args.get("sort", "popularity"),
    )
    return jsonify({"tracks": tracks, "total": len(tracks)}), 200


@tracks_bp.get("/meta")
def get_meta():
    meta = get_catalog_metadata(current_app.config.get("DATABASE_PATH"))
    return jsonify(meta), 200
