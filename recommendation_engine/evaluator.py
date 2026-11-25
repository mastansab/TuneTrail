"""Offline evaluation script for TuneTrail Hybrid Recommendation Engine."""

import json
from collections import defaultdict

from recommendation_engine.hybrid import HybridRecommender


def evaluate_recommender(
    tracks: list[dict],
    history: list[dict],
    favourites: list[dict],
    users_prefs: dict[int, tuple[list[str], list[str]]],
    k: int = 10,
    holdout_n: int = 2,
    alpha: float = 0.6,
) -> dict:
    """Evaluate recommendation Hit Rate@K, Precision@K, Recall@K, and Diversity on held-out plays."""
    if not tracks or not history:
        return {"users_evaluated": 0, "hit_rate_at_k": 0.0}

    by_user: dict[int, list[dict]] = defaultdict(list)
    for row in history:
        by_user[int(row["user_id"])].append(row)

    train_history: list[dict] = []
    holdout_by_user: dict[int, set[int]] = {}

    for uid, rows in by_user.items():
        ordered = sorted(rows, key=lambda r: str(r.get("played_at", "")))
        if len(ordered) >= 5:
            train_history.extend(ordered[:-holdout_n])
            holdout_by_user[uid] = {int(r["track_id"]) for r in ordered[-holdout_n:]}
        else:
            train_history.extend(ordered)

    if not holdout_by_user:
        return {"users_evaluated": 0, "hit_rate_at_k": 0.0}

    recommender = HybridRecommender(tracks, train_history, favourites)

    hits = 0
    precisions = []
    recalls = []
    recommended_all: set[int] = set()
    genre_diversities = []

    for uid, ground_truth in holdout_by_user.items():
        pref_genres, pref_artists = users_prefs.get(uid, ([], []))
        train_played = {int(r["track_id"]) for r in train_history if int(r["user_id"]) == uid}
        res = recommender.recommend(
            user_id=uid,
            preferred_genres=pref_genres,
            preferred_artists=pref_artists,
            alpha=alpha,
            mode="hybrid",
            limit=k + len(train_played),
            exclude_recent=False,
        )
        recs = [r for r in res["recommendations"] if r["id"] not in train_played][:k]
        rec_ids = [r["id"] for r in recs]
        recommended_all.update(rec_ids)

        matched = len(set(rec_ids) & ground_truth)
        if matched > 0:
            hits += 1
        precisions.append(matched / max(len(rec_ids), 1))
        recalls.append(matched / max(len(ground_truth), 1))
        genre_diversities.append(len({r["genre"] for r in recs}))

    n_users = len(holdout_by_user)
    return {
        "k": k,
        "alpha": alpha,
        "users_evaluated": n_users,
        "hit_rate_at_k": round(hits / n_users, 4),
        "precision_at_k": round(sum(precisions) / n_users, 4),
        "recall_at_k": round(sum(recalls) / n_users, 4),
        "catalog_coverage": round(len(recommended_all) / max(len(tracks), 1), 4),
        "avg_genre_diversity": round(sum(genre_diversities) / n_users, 2),
    }


if __name__ == "__main__":
    from database.db import db_session

    with db_session() as conn:
        tracks = [dict(r) for r in conn.execute("SELECT * FROM Tracks").fetchall()]
        history = [dict(r) for r in conn.execute("SELECT * FROM ListeningHistory").fetchall()]
        favs = [dict(r) for r in conn.execute("SELECT * FROM Favourites").fetchall()]
        prefs_rows = conn.execute("SELECT user_id, preferred_genres, preferred_artists FROM UserPreferences").fetchall()

    prefs_map = {
        int(r["user_id"]): (json.loads(r["preferred_genres"]), json.loads(r["preferred_artists"]))
        for r in prefs_rows
    }
    metrics = evaluate_recommender(tracks, history, favs, prefs_map)
    print(json.dumps(metrics, indent=2))
