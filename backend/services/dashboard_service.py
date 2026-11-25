"""Dashboard analytics and aggregation service."""

from pathlib import Path

from backend.services.music_service import get_favourites, get_listening_history
from backend.services.recommendation_service import get_recommendations_for_user
from database.db import db_session


def get_dashboard_data(db_path: str | Path | None, user_id: int) -> dict:
    """Aggregate KPIs, genre distribution, listening activity, and recommendations."""
    with db_session(db_path) as conn:
        total_tracks = conn.execute("SELECT COUNT(*) FROM Tracks").fetchone()[0]
        total_playlists = conn.execute(
            "SELECT COUNT(*) FROM Playlists WHERE user_id = ?", (user_id,)
        ).fetchone()[0]
        total_plays = conn.execute(
            "SELECT COUNT(*) FROM ListeningHistory WHERE user_id = ?", (user_id,)
        ).fetchone()[0]

        # Genre distribution: user's listening if available, else catalog distribution
        user_genres = conn.execute(
            """
            SELECT t.genre, COUNT(*) AS count
            FROM ListeningHistory lh
            JOIN Tracks t ON t.id = lh.track_id
            WHERE lh.user_id = ?
            GROUP BY t.genre
            ORDER BY count DESC
            """,
            (user_id,),
        ).fetchall()

        if user_genres:
            genre_distribution = [dict(r) for r in user_genres]
            genre_source = "user_history"
        else:
            catalog_genres = conn.execute(
                "SELECT genre, COUNT(*) AS count FROM Tracks GROUP BY genre ORDER BY count DESC"
            ).fetchall()
            genre_distribution = [dict(r) for r in catalog_genres]
            genre_source = "catalog"

        activity_rows = conn.execute(
            """
            SELECT date(played_at) AS day, COUNT(*) AS plays
            FROM ListeningHistory
            WHERE user_id = ?
            GROUP BY date(played_at)
            ORDER BY day ASC
            LIMIT 14
            """,
            (user_id,),
        ).fetchall()

    favourites = get_favourites(db_path, user_id)
    recent_plays = get_listening_history(db_path, user_id, limit=6)
    rec_result = get_recommendations_for_user(db_path, user_id, mode="hybrid", limit=6)

    return {
        "summary": {
            "total_tracks": total_tracks,
            "total_playlists": total_playlists,
            "total_plays": total_plays,
            "total_favourites": len(favourites),
        },
        "genre_distribution": genre_distribution,
        "genre_source": genre_source,
        "listening_activity": [dict(r) for r in activity_rows],
        "recently_played": recent_plays,
        "favourites": favourites[:6],
        "recommendations": rec_result["recommendations"],
        "recommendation_meta": rec_result["meta"],
    }
