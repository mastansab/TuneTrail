"""Hybrid Recommendation Engine combining Content-Based & Collaborative Filtering."""

import numpy as np

from recommendation_engine.collaborative import CollaborativeRecommender
from recommendation_engine.content_based import ContentBasedRecommender


class HybridRecommender:
    """Combines Content-Based and Collaborative Filtering with diversity & anti-repetition."""

    def __init__(
        self,
        tracks: list[dict],
        all_history: list[dict],
        all_favourites: list[dict],
    ):
        self.tracks = list(tracks)
        self.all_history = list(all_history)
        self.all_favourites = list(all_favourites)
        self.cb_engine = ContentBasedRecommender(self.tracks)
        self.cf_engine = CollaborativeRecommender(
            self.tracks, self.all_history, self.all_favourites
        )

    def recommend(
        self,
        user_id: int,
        preferred_genres: list[str] | None = None,
        preferred_artists: list[str] | None = None,
        alpha: float = 0.6,
        mode: str = "hybrid",
        limit: int = 10,
        exclude_recent: bool = True,
        avoid_recent_count: int = 5,
    ) -> dict:
        """Generate personalized, diverse, explainable music recommendations."""
        if not self.tracks:
            return {"recommendations": [], "meta": {"mode": mode, "alpha": alpha, "cold_start": True}}

        alpha = float(np.clip(alpha, 0.0, 1.0))
        user_history = [r for r in self.all_history if int(r["user_id"]) == int(user_id)]
        user_favs = {int(r["track_id"]) for r in self.all_favourites if int(r["user_id"]) == int(user_id)}

        cb_scores, cb_reasons, _ = self.cb_engine.score_tracks(
            history_rows=user_history,
            favourites_ids=user_favs,
            preferred_genres=preferred_genres,
            preferred_artists=preferred_artists,
        )
        cf_scores, cf_reasons, cf_meta = self.cf_engine.score_tracks(target_user_id=user_id)

        is_cf_cold_start = bool(cf_meta.get("cold_start", True))

        if mode == "content":
            effective_alpha = 1.0
        elif mode == "collaborative":
            effective_alpha = 1.0 if is_cf_cold_start else 0.0
        else:
            effective_alpha = 1.0 if is_cf_cold_start else alpha

        combined_scores = effective_alpha * cb_scores + (1.0 - effective_alpha) * cf_scores

        recent_track_ids: set[int] = set()
        if exclude_recent and user_history and avoid_recent_count > 0:
            recent_sorted = sorted(user_history, key=lambda r: str(r.get("played_at", "")), reverse=True)
            recent_track_ids = {int(r["track_id"]) for r in recent_sorted[:avoid_recent_count]}

        candidate_indices = [
            idx for idx, t in enumerate(self.tracks)
            if int(t["id"]) not in recent_track_ids
        ]
        if len(candidate_indices) < limit:
            candidate_indices = list(range(len(self.tracks)))

        selected = []
        remaining = set(candidate_indices)
        artist_counts: dict[str, int] = {}
        genre_counts: dict[str, int] = {}

        while remaining and len(selected) < limit:
            best_idx = None
            best_adj_score = -1.0
            for idx in remaining:
                artist = str(self.tracks[idx]["artist"])
                genre = str(self.tracks[idx]["genre"])
                diversity_penalty = (0.82 ** artist_counts.get(artist, 0)) * (0.92 ** genre_counts.get(genre, 0))
                adj_score = float(combined_scores[idx]) * diversity_penalty
                if adj_score > best_adj_score:
                    best_adj_score = adj_score
                    best_idx = idx

            if best_idx is None:
                break

            remaining.remove(best_idx)
            row = self.tracks[best_idx]
            artist = str(row["artist"])
            genre = str(row["genre"])
            artist_counts[artist] = artist_counts.get(artist, 0) + 1
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

            cb_val = round(float(cb_scores[best_idx]), 4)
            cf_val = round(float(cf_scores[best_idx]), 4)
            hyb_val = round(float(combined_scores[best_idx]), 4)

            reasons = [cb_reasons[best_idx]]
            if not is_cf_cold_start and cf_val > 0.15:
                reasons.append(cf_reasons[best_idx])

            track_dict = {
                "id": int(row["id"]),
                "title": str(row["title"]),
                "artist": artist,
                "album": str(row["album"]),
                "genre": genre,
                "release_year": int(row["release_year"]),
                "duration_sec": int(row["duration_sec"]),
                "tempo": float(row["tempo"]),
                "energy": float(row["energy"]),
                "danceability": float(row["danceability"]),
                "valence": float(row["valence"]),
                "acousticness": float(row["acousticness"]),
                "popularity": int(row["popularity"]),
                "cover_color": str(row["cover_color"]),
                "tags": str(row["tags"]),
                "is_favourite": int(row["id"]) in user_favs,
                "scores": {
                    "content": cb_val,
                    "collaborative": cf_val,
                    "hybrid": hyb_val,
                    "match_percent": min(99, max(50, int(round(hyb_val * 100)))),
                },
                "explanation": " • ".join(reasons),
                "reasons": reasons,
            }
            selected.append(track_dict)

        return {
            "recommendations": selected,
            "meta": {
                "mode": mode,
                "requested_alpha": alpha,
                "effective_alpha": effective_alpha,
                "cold_start": is_cf_cold_start,
                "neighbor_count": cf_meta.get("neighbor_count", 0),
                "excluded_recent_count": len(recent_track_ids),
                "diversity_genres": len(genre_counts),
                "diversity_artists": len(artist_counts),
            },
        }
