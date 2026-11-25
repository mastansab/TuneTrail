"""Service wrapper connecting SQLite data to the AI/ML Recommendation Engine."""

import json
from pathlib import Path

from backend.services.auth_service import get_preferences
from database.db import db_session
from recommendation_engine.evaluator import evaluate_recommender
from recommendation_engine.hybrid import HybridRecommender


def _load_engine_data(db_path: str | Path | None) -> tuple[list[dict], list[dict], list[dict]]:
    with db_session(db_path) as conn:
        tracks = [dict(r) for r in conn.execute("SELECT * FROM Tracks").fetchall()]
        history = [dict(r) for r in conn.execute("SELECT * FROM ListeningHistory").fetchall()]
        favourites = [dict(r) for r in conn.execute("SELECT * FROM Favourites").fetchall()]
    return tracks, history, favourites


def get_recommendations_for_user(
    db_path: str | Path | None,
    user_id: int,
    mode: str = "hybrid",
    alpha: float | None = None,
    limit: int = 10,
    exclude_recent: bool = True,
) -> dict:
    """Generate personalized recommendations for a user."""
    prefs = get_preferences(db_path, user_id)
    effective_alpha = prefs["hybrid_alpha"] if alpha is None else float(alpha)
    tracks, history, favourites = _load_engine_data(db_path)

    engine = HybridRecommender(tracks, history, favourites)
    return engine.recommend(
        user_id=user_id,
        preferred_genres=prefs["preferred_genres"],
        preferred_artists=prefs["preferred_artists"],
        alpha=effective_alpha,
        mode=mode,
        limit=limit,
        exclude_recent=exclude_recent,
        avoid_recent_count=prefs["avoid_recent_count"],
    )


def run_offline_evaluation(db_path: str | Path | None, k: int = 10, alpha: float = 0.6) -> dict:
    """Run held-out evaluation on the current database state."""
    tracks, history, favourites = _load_engine_data(db_path)
    with db_session(db_path) as conn:
        prefs_rows = conn.execute(
            "SELECT user_id, preferred_genres, preferred_artists FROM UserPreferences"
        ).fetchall()
    prefs_map = {
        int(r["user_id"]): (json.loads(r["preferred_genres"]), json.loads(r["preferred_artists"]))
        for r in prefs_rows
    }
    return evaluate_recommender(tracks, history, favourites, prefs_map, k=k, alpha=alpha)
