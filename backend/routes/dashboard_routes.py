"""Dashboard analytics route."""

from flask import Blueprint, current_app, g, jsonify

from backend.services.dashboard_service import get_dashboard_data
from backend.utils.auth import require_auth

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.get("")
@require_auth
def dashboard():
    data = get_dashboard_data(current_app.config.get("DATABASE_PATH"), g.current_user["id"])
    return jsonify(data), 200
