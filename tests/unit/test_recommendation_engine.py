"""Unit tests for Content-Based, Collaborative, Hybrid, and Offline Evaluation."""

import json
from database.db import db_session
from recommendation_engine.collaborative import CollaborativeRecommender
from recommendation_engine.content_based import ContentBasedRecommender
from recommendation_engine.evaluator import evaluate_recommender
from recommendation_engine.hybrid import HybridRecommender


def _load_data(db_path):
    with db_session(db_path) as conn:
        tracks = [dict(r) for r in conn.execute("SELECT * FROM Tracks").fetchall()]
        history = [dict(r) for r in conn.execute("SELECT * FROM ListeningHistory").fetchall()]
        favs = [dict(r) for r in conn.execute("SELECT * FROM Favourites").fetchall()]
        prefs_rows = conn.execute("SELECT user_id, preferred_genres, preferred_artists FROM UserPreferences").fetchall()
        demo_id = conn.execute("SELECT id FROM Users WHERE username = 'demo'").fetchone()["id"]
        newbie_id = conn.execute("SELECT id FROM Users WHERE username = 'newbie'").fetchone()["id"]
    prefs_map = {
        int(r["user_id"]): (json.loads(r["preferred_genres"]), json.loads(r["preferred_artists"]))
        for r in prefs_rows
    }
    return tracks, history, favs, prefs_map, demo_id, newbie_id


def test_content_based_prefers_matching_genres(test_db):
    tracks, history, favs, _, demo_id, _ = _load_data(test_db)
    cb = ContentBasedRecommender(tracks)
    user_hist = [h for h in history if h["user_id"] == demo_id]
    user_favs = {f["track_id"] for f in favs if f["user_id"] == demo_id}

    scores, reasons, meta = cb.score_tracks(user_hist, user_favs, ["Synthwave"], ["Midnight Pulse"])
    assert len(scores) == len(tracks)
    assert 0.0 <= float(scores.min()) <= float(scores.max()) <= 1.0
    assert meta["cold_start"] is False
    assert len(reasons) == len(tracks)


def test_collaborative_finds_similar_users_and_detects_cold_start(test_db):
    tracks, history, favs, _, demo_id, newbie_id = _load_data(test_db)
    cf = CollaborativeRecommender(tracks, history, favs)

    scores_demo, _, meta_demo = cf.score_tracks(demo_id)
    assert meta_demo["cold_start"] is False
    assert meta_demo["neighbor_count"] >= 1
    assert float(scores_demo.max()) > 0.0

    scores_new, _, meta_new = cf.score_tracks(newbie_id)
    assert meta_new["cold_start"] is True
    assert float(scores_new.max()) == 0.0


def test_hybrid_modes_anti_repetition_and_cold_start(test_db):
    tracks, history, favs, prefs_map, demo_id, newbie_id = _load_data(test_db)
    engine = HybridRecommender(tracks, history, favs)

    # Active user hybrid recommendations
    res = engine.recommend(
        user_id=demo_id,
        preferred_genres=prefs_map[demo_id][0],
        preferred_artists=prefs_map[demo_id][1],
        alpha=0.6,
        mode="hybrid",
        limit=10,
        exclude_recent=True,
        avoid_recent_count=5,
    )
    recs = res["recommendations"]
    assert len(recs) == 10
    assert res["meta"]["cold_start"] is False
    assert res["meta"]["diversity_genres"] >= 2

    # Ensure top 5 most recent tracks were excluded
    demo_recent = [
        h["track_id"]
        for h in sorted([h for h in history if h["user_id"] == demo_id], key=lambda x: str(x["played_at"]), reverse=True)[:5]
    ]
    rec_ids = {r["id"] for r in recs}
    assert rec_ids.isdisjoint(set(demo_recent))

    # Cold-start user falls back smoothly to content-based with preferences
    res_new = engine.recommend(
        user_id=newbie_id,
        preferred_genres=prefs_map[newbie_id][0],
        preferred_artists=prefs_map[newbie_id][1],
        alpha=0.6,
        mode="hybrid",
        limit=8,
    )
    assert len(res_new["recommendations"]) == 8
    assert res_new["meta"]["cold_start"] is True
    assert res_new["meta"]["effective_alpha"] == 1.0


def test_offline_evaluation_meets_target_hit_rate(test_db):
    tracks, history, favs, prefs_map, _, _ = _load_data(test_db)
    metrics = evaluate_recommender(tracks, history, favs, prefs_map, k=10, alpha=0.6)
    assert metrics["users_evaluated"] >= 10
    assert metrics["hit_rate_at_k"] >= 0.50
