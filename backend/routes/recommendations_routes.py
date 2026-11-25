"""AI Recommendation Engine API routes."""

from flask import Blueprint, current_app, g, jsonify, request

from backend.services.recommendation_service import (
    get_recommendations_for_user,
    run_offline_evaluation,
)
from backend.utils.auth import require_auth

recommendations_bp = Blueprint("recommendations", __name__, url_prefix="/api/recommendations")


@recommendations_bp.get("")
@require_auth
def recommend():
    mode = request.args.get("mode", "hybrid").lower()
    if mode not in ("hybrid", "content", "collaborative"):
        return jsonify({"error": "mode must be hybrid, content, or collaborative"}), 400

    alpha_param = request.args.get("alpha")
    alpha = float(alpha_param) if alpha_param is not None else None
    limit = min(30, max(1, int(request.args.get("limit", 10))))
    exclude_recent = request.args.get("exclude_recent", "true").lower() != "false"

    result = get_recommendations_for_user(
        db_path=current_app.config.get("DATABASE_PATH"),
        user_id=g.current_user["id"],
        mode=mode,
        alpha=alpha,
        limit=limit,
        exclude_recent=exclude_recent,
    )
    return jsonify(result), 200


@recommendations_bp.get("/evaluate")
@require_auth
def evaluate():
    k = min(20, max(1, int(request.args.get("k", 10))))
    alpha = float(request.args.get("alpha", current_app.config.get("HYBRID_ALPHA", 0.6)))
    metrics = run_offline_evaluation(current_app.config.get("DATABASE_PATH"), k=k, alpha=alpha)
    return jsonify(metrics), 200
