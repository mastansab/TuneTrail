"""Authentication and user profile routes."""

from flask import Blueprint, current_app, g, jsonify, request, session

from backend.services.auth_service import (
    get_preferences,
    login_user,
    register_user,
    update_profile_and_preferences,
)
from backend.utils.auth import require_auth

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    payload, status = register_user(
        db_path=current_app.config.get("DATABASE_PATH"),
        secret_key=current_app.config["SECRET_KEY"],
        username=data.get("username", ""),
        email=data.get("email", ""),
        password=data.get("password", ""),
        display_name=data.get("display_name"),
        preferred_genres=data.get("preferred_genres"),
        preferred_artists=data.get("preferred_artists"),
    )
    if status == 201:
        session["user_id"] = payload["user"]["id"]
    return jsonify(payload), status


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    identifier = data.get("identifier") or data.get("username") or data.get("email") or ""
    payload, status = login_user(
        db_path=current_app.config.get("DATABASE_PATH"),
        secret_key=current_app.config["SECRET_KEY"],
        identifier=identifier,
        password=data.get("password", ""),
    )
    if status == 200:
        session["user_id"] = payload["user"]["id"]
    return jsonify(payload), status


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.get("/me")
@require_auth
def me():
    prefs = get_preferences(current_app.config.get("DATABASE_PATH"), g.current_user["id"])
    return jsonify({"user": g.current_user, "preferences": prefs}), 200


@auth_bp.put("/profile")
@require_auth
def update_profile():
    data = request.get_json(silent=True) or {}
    payload, status = update_profile_and_preferences(
        db_path=current_app.config.get("DATABASE_PATH"),
        user_id=g.current_user["id"],
        display_name=data.get("display_name"),
        preferred_genres=data.get("preferred_genres"),
        preferred_artists=data.get("preferred_artists"),
        hybrid_alpha=data.get("hybrid_alpha"),
        avoid_recent_count=data.get("avoid_recent_count"),
    )
    return jsonify(payload), status
