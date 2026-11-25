"""Collaborative Filtering recommender using User-User Cosine Similarity."""

import numpy as np


class CollaborativeRecommender:
    """Recommends tracks based on similar users' listening histories and favourites."""

    def __init__(
        self,
        tracks: list[dict],
        all_history: list[dict],
        all_favourites: list[dict],
    ):
        self.tracks = list(tracks)
        self.track_ids = [int(t["id"]) for t in self.tracks]
        self.track_id_to_idx = {tid: idx for idx, tid in enumerate(self.track_ids)}
        self.all_history = list(all_history)
        self.all_favourites = list(all_favourites)

    def score_tracks(self, target_user_id: int, k_neighbors: int = 5) -> tuple[np.ndarray, list[str], dict]:
        """Compute collaborative filtering scores [0, 1] and explanations for target_user_id."""
        n_tracks = len(self.tracks)
        if n_tracks == 0:
            return np.array([]), [], {"cold_start": True, "neighbor_count": 0}

        user_ids_set = {int(r["user_id"]) for r in self.all_history}
        user_ids_set.update(int(r["user_id"]) for r in self.all_favourites)
        user_ids_set.add(int(target_user_id))

        user_ids = sorted(user_ids_set)
        user_to_row = {uid: r for r, uid in enumerate(user_ids)}
        matrix = np.zeros((len(user_ids), n_tracks), dtype=float)

        for row in self.all_history:
            u_idx = user_to_row.get(int(row["user_id"]))
            t_idx = self.track_id_to_idx.get(int(row["track_id"]))
            if u_idx is not None and t_idx is not None:
                weight = 1.0 if int(row.get("completed", 1)) == 1 else 0.5
                matrix[u_idx, t_idx] += weight

        for row in self.all_favourites:
            u_idx = user_to_row.get(int(row["user_id"]))
            t_idx = self.track_id_to_idx.get(int(row["track_id"]))
            if u_idx is not None and t_idx is not None:
                matrix[u_idx, t_idx] += 2.0

        target_row = user_to_row[int(target_user_id)]
        target_vec = matrix[target_row]
        target_interactions = int(np.count_nonzero(target_vec))

        if target_interactions < 2 or len(user_ids) < 2:
            return (
                np.zeros(n_tracks, dtype=float),
                ["Insufficient listening history for collaborative matching"] * n_tracks,
                {"cold_start": True, "neighbor_count": 0, "user_interactions": target_interactions},
            )

        target_norm = float(np.linalg.norm(target_vec))
        row_norms = np.linalg.norm(matrix, axis=1)
        row_norms[row_norms == 0] = 1.0
        sims = (matrix @ target_vec) / (row_norms * max(target_norm, 1e-8))
        sims[target_row] = -1.0

        neighbor_indices = [
            int(idx) for idx in np.argsort(sims)[::-1][:k_neighbors]
            if sims[idx] > 0.05
        ]

        if not neighbor_indices:
            return (
                np.zeros(n_tracks, dtype=float),
                ["No similar listeners found yet"] * n_tracks,
                {"cold_start": True, "neighbor_count": 0, "user_interactions": target_interactions},
            )

        weighted_scores = np.zeros(n_tracks, dtype=float)
        supporter_counts = np.zeros(n_tracks, dtype=int)
        sim_sum = sum(float(sims[idx]) for idx in neighbor_indices)

        for n_idx in neighbor_indices:
            sim = float(sims[n_idx])
            weighted_scores += sim * matrix[n_idx]
            supporter_counts += (matrix[n_idx] > 0).astype(int)

        if sim_sum > 0:
            weighted_scores /= sim_sum

        max_score = float(weighted_scores.max())
        if max_score > 1e-8:
            scores = weighted_scores / max_score
        else:
            scores = np.zeros(n_tracks, dtype=float)

        reasons = []
        for idx in range(n_tracks):
            cnt = int(supporter_counts[idx])
            if cnt > 0:
                reasons.append(f"Enjoyed by {cnt} listener{'s' if cnt > 1 else ''} with similar taste")
            else:
                reasons.append("Emerging discovery outside your current circle")

        return scores, reasons, {
            "cold_start": False,
            "neighbor_count": len(neighbor_indices),
            "user_interactions": target_interactions,
        }
