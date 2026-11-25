"""Content-Based Filtering recommender using TF-IDF metadata + scaled audio features."""

import math
import re
from collections import Counter
import numpy as np

AUDIO_FEATURES = ["tempo", "energy", "danceability", "valence", "acousticness", "release_year"]
STOP_WORDS = {"the", "a", "an", "and", "or", "of", "in", "on", "to", "for", "with", "at", "by"}


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in tokens if len(t) > 1 and t not in STOP_WORDS]


def _build_tfidf_matrix(documents: list[str], max_features: int = 300) -> np.ndarray:
    """Compute L2-normalized TF-IDF matrix using NumPy."""
    n_docs = len(documents)
    if n_docs == 0:
        return np.zeros((0, 1), dtype=float)

    tokenized = [_tokenize(doc) for doc in documents]
    df_counts: Counter[str] = Counter()
    for tokens in tokenized:
        df_counts.update(set(tokens))

    vocab = [term for term, _ in df_counts.most_common(max_features)]
    term_to_idx = {term: idx for idx, term in enumerate(vocab)}
    n_terms = max(len(vocab), 1)

    mat = np.zeros((n_docs, n_terms), dtype=float)
    for row_idx, tokens in enumerate(tokenized):
        if not tokens:
            continue
        tf = Counter(tokens)
        for term, count in tf.items():
            col_idx = term_to_idx.get(term)
            if col_idx is not None:
                idf = math.log((1.0 + n_docs) / (1.0 + df_counts[term])) + 1.0
                mat[row_idx, col_idx] = (count / len(tokens)) * idf

    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return mat / norms


def _standardize_matrix(values: np.ndarray) -> np.ndarray:
    """Zero-mean, unit-variance standardization using NumPy."""
    if values.size == 0:
        return values
    mean = values.mean(axis=0, keepdims=True)
    std = values.std(axis=0, keepdims=True)
    std[std == 0] = 1.0
    return (values - mean) / std


def _cosine_sim_vector(vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between a 1D vector and each row of matrix."""
    v_norm = float(np.linalg.norm(vec))
    if v_norm == 0.0:
        return np.zeros(matrix.shape[0], dtype=float)
    m_norms = np.linalg.norm(matrix, axis=1)
    m_norms[m_norms == 0] = 1.0
    return (matrix @ vec) / (m_norms * v_norm)


class ContentBasedRecommender:
    """Recommends tracks based on genre, artist, tags, and audio characteristics."""

    def __init__(self, tracks: list[dict]):
        self.tracks = list(tracks)
        self.track_id_to_idx = {int(t["id"]): idx for idx, t in enumerate(self.tracks)}
        self.feature_matrix = self._build_feature_matrix()

    def _build_feature_matrix(self) -> np.ndarray:
        if not self.tracks:
            return np.zeros((0, 1), dtype=float)

        documents = [
            f"{t.get('genre', '')} {t.get('genre', '')} {t.get('artist', '')} "
            f"{t.get('album', '')} {str(t.get('tags', '')).replace(',', ' ')}"
            for t in self.tracks
        ]
        text_matrix = _build_tfidf_matrix(documents, max_features=300)

        audio_raw = np.array(
            [[float(t[feat]) for feat in AUDIO_FEATURES] for t in self.tracks],
            dtype=float,
        )
        audio_matrix = _standardize_matrix(audio_raw)

        combined = np.hstack([text_matrix * 1.4, audio_matrix * 0.8])
        norms = np.linalg.norm(combined, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return combined / norms

    def score_tracks(
        self,
        history_rows: list[dict],
        favourites_ids: set[int],
        preferred_genres: list[str] | None = None,
        preferred_artists: list[str] | None = None,
    ) -> tuple[np.ndarray, list[str], dict]:
        """Compute content-based similarity scores [0, 1] and explanations for all tracks."""
        n_tracks = len(self.tracks)
        if n_tracks == 0:
            return np.array([]), [], {"cold_start": True}

        preferred_genres = preferred_genres or []
        preferred_artists = preferred_artists or []
        profile_vec = np.zeros(self.feature_matrix.shape[1], dtype=float)
        total_weight = 0.0

        top_genres: dict[str, float] = {}
        top_artists: dict[str, float] = {}

        # 1. Weight listening history (with recency decay)
        if history_rows:
            hist_sorted = sorted(history_rows, key=lambda r: str(r.get("played_at", "")), reverse=True)
            for rank, row in enumerate(hist_sorted):
                tid = int(row["track_id"])
                idx = self.track_id_to_idx.get(tid)
                if idx is None:
                    continue
                recency_decay = 1.0 / (1.0 + 0.08 * rank)
                completion_bonus = 1.3 if int(row.get("completed", 1)) == 1 else 0.7
                w = recency_decay * completion_bonus
                profile_vec += w * self.feature_matrix[idx]
                total_weight += w
                g = str(self.tracks[idx]["genre"])
                a = str(self.tracks[idx]["artist"])
                top_genres[g] = top_genres.get(g, 0.0) + w
                top_artists[a] = top_artists.get(a, 0.0) + w

        # 2. Weight favourites strongly
        for tid in favourites_ids:
            idx = self.track_id_to_idx.get(int(tid))
            if idx is not None:
                w = 2.0
                profile_vec += w * self.feature_matrix[idx]
                total_weight += w
                g = str(self.tracks[idx]["genre"])
                a = str(self.tracks[idx]["artist"])
                top_genres[g] = top_genres.get(g, 0.0) + w
                top_artists[a] = top_artists.get(a, 0.0) + w

        # 3. Weight explicit user preferences (essential for cold-start)
        if preferred_genres or preferred_artists:
            for idx, row in enumerate(self.tracks):
                w = 0.0
                if row["genre"] in preferred_genres:
                    w += 1.2
                    top_genres[row["genre"]] = top_genres.get(row["genre"], 0.0) + 1.2
                if row["artist"] in preferred_artists:
                    w += 1.5
                    top_artists[row["artist"]] = top_artists.get(row["artist"], 0.0) + 1.5
                if w > 0:
                    profile_vec += w * self.feature_matrix[idx]
                    total_weight += w

        used_fallback = False
        if total_weight == 0.0:
            used_fallback = True
            pop = np.array([float(t["popularity"]) for t in self.tracks], dtype=float)
            scores = (pop - pop.min()) / max(float(pop.max() - pop.min()), 1.0)
            reasons = [
                f"Popular {t['genre']} pick while we learn your taste"
                for t in self.tracks
            ]
            return scores, reasons, {"cold_start": True, "used_popularity_fallback": True}

        profile_norm = float(np.linalg.norm(profile_vec))
        if profile_norm > 0:
            profile_vec = profile_vec / profile_norm

        raw_sims = _cosine_sim_vector(profile_vec, self.feature_matrix)
        min_s, max_s = float(raw_sims.min()), float(raw_sims.max())
        if max_s - min_s > 1e-8:
            scores = (raw_sims - min_s) / (max_s - min_s)
        else:
            scores = np.clip(raw_sims, 0.0, 1.0)

        fav_genres = {g for g, _ in sorted(top_genres.items(), key=lambda x: x[1], reverse=True)[:3]}
        fav_artists = {a for a, _ in sorted(top_artists.items(), key=lambda x: x[1], reverse=True)[:3]}

        reasons = []
        for row in self.tracks:
            parts = []
            if row["artist"] in fav_artists:
                parts.append(f"artist {row['artist']}")
            if row["genre"] in fav_genres:
                parts.append(f"{row['genre']} genre")
            if not parts:
                parts.append(f"similar audio profile ({int(row['tempo'])} BPM, {row['genre']})")
            reasons.append("Matches your taste in " + " & ".join(parts))

        return scores, reasons, {
            "cold_start": used_fallback,
            "top_genres": list(fav_genres),
            "top_artists": list(fav_artists),
        }
