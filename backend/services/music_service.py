"""Music catalog, favourites, playlists, and listening history service."""

import sqlite3
from pathlib import Path
from database.db import db_session


def list_tracks(
    db_path: str | Path | None,
    user_id: int | None = None,
    query: str = "",
    genre: str = "",
    artist: str = "",
    sort_by: str = "popularity",
) -> list[dict]:
    """Search and filter music tracks, annotated with user's favourite status."""
    sql = "SELECT * FROM Tracks WHERE 1=1"
    params: list = []

    if query.strip():
        like = f"%{query.strip()}%"
        sql += " AND (lower(title) LIKE lower(?) OR lower(artist) LIKE lower(?) OR lower(tags) LIKE lower(?))"
        params.extend([like, like, like])
    if genre.strip() and genre.strip().lower() != "all":
        sql += " AND lower(genre) = lower(?)"
        params.append(genre.strip())
    if artist.strip() and artist.strip().lower() != "all":
        sql += " AND lower(artist) = lower(?)"
        params.append(artist.strip())

    order_map = {
        "popularity": "popularity DESC, id ASC",
        "title": "title ASC",
        "artist": "artist ASC",
        "newest": "release_year DESC, id DESC",
        "tempo": "tempo DESC",
    }
    sql += f" ORDER BY {order_map.get(sort_by, 'popularity DESC, id ASC')}"

    with db_session(db_path) as conn:
        rows = conn.execute(sql, params).fetchall()
        fav_ids = set()
        if user_id is not None:
            fav_rows = conn.execute("SELECT track_id FROM Favourites WHERE user_id = ?", (user_id,)).fetchall()
            fav_ids = {int(r["track_id"]) for r in fav_rows}

    tracks = []
    for r in rows:
        d = dict(r)
        d["is_favourite"] = d["id"] in fav_ids
        tracks.append(d)
    return tracks


def get_catalog_metadata(db_path: str | Path | None) -> dict:
    """Return distinct genres and artists available in the catalog."""
    with db_session(db_path) as conn:
        genres = [r["genre"] for r in conn.execute("SELECT DISTINCT genre FROM Tracks ORDER BY genre").fetchall()]
        artists = [r["artist"] for r in conn.execute("SELECT DISTINCT artist FROM Tracks ORDER BY artist").fetchall()]
    return {"genres": genres, "artists": artists}


def get_favourites(db_path: str | Path | None, user_id: int) -> list[dict]:
    """Return all favourite tracks for a user."""
    with db_session(db_path) as conn:
        rows = conn.execute(
            """
            SELECT t.*, f.created_at AS favourited_at
            FROM Favourites f
            JOIN Tracks t ON t.id = f.track_id
            WHERE f.user_id = ?
            ORDER BY f.created_at DESC
            """,
            (user_id,),
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["is_favourite"] = True
        d["favourited_at"] = str(d["favourited_at"])
        result.append(d)
    return result


def add_favourite(db_path: str | Path | None, user_id: int, track_id: int) -> tuple[dict, int]:
    """Add a track to user's favourites."""
    with db_session(db_path) as conn:
        track = conn.execute("SELECT id FROM Tracks WHERE id = ?", (track_id,)).fetchone()
        if track is None:
            return {"error": "Track not found"}, 404
        conn.execute(
            "INSERT OR IGNORE INTO Favourites (user_id, track_id) VALUES (?, ?)",
            (user_id, track_id),
        )
    return {"message": "Added to favourites", "track_id": track_id, "is_favourite": True}, 201


def remove_favourite(db_path: str | Path | None, user_id: int, track_id: int) -> tuple[dict, int]:
    """Remove a track from user's favourites."""
    with db_session(db_path) as conn:
        conn.execute(
            "DELETE FROM Favourites WHERE user_id = ? AND track_id = ?",
            (user_id, track_id),
        )
    return {"message": "Removed from favourites", "track_id": track_id, "is_favourite": False}, 200


def get_playlists(db_path: str | Path | None, user_id: int) -> list[dict]:
    """Return all playlists owned by user with track counts and tracks."""
    with db_session(db_path) as conn:
        playlists = conn.execute(
            "SELECT * FROM Playlists WHERE user_id = ? ORDER BY updated_at DESC, id DESC",
            (user_id,),
        ).fetchall()
        result = []
        for p in playlists:
            p_dict = dict(p)
            p_dict["created_at"] = str(p_dict["created_at"])
            p_dict["updated_at"] = str(p_dict["updated_at"])
            tracks = conn.execute(
                """
                SELECT t.*, pt.position, pt.added_at
                FROM PlaylistTracks pt
                JOIN Tracks t ON t.id = pt.track_id
                WHERE pt.playlist_id = ?
                ORDER BY pt.position ASC, pt.added_at ASC
                """,
                (p["id"],),
            ).fetchall()
            p_dict["tracks"] = [dict(t) for t in tracks]
            p_dict["track_count"] = len(p_dict["tracks"])
            result.append(p_dict)
    return result


def create_playlist(
    db_path: str | Path | None, user_id: int, name: str, description: str = ""
) -> tuple[dict, int]:
    """Create a new playlist for the user."""
    name = (name or "").strip()
    if not name:
        return {"error": "Playlist name is required"}, 400
    with db_session(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO Playlists (user_id, name, description) VALUES (?, ?, ?)",
            (user_id, name, (description or "").strip()),
        )
        pid = cur.lastrowid
        row = dict(conn.execute("SELECT * FROM Playlists WHERE id = ?", (pid,)).fetchone())
    row["tracks"] = []
    row["track_count"] = 0
    row["created_at"] = str(row["created_at"])
    row["updated_at"] = str(row["updated_at"])
    return {"playlist": row}, 201


def delete_playlist(db_path: str | Path | None, user_id: int, playlist_id: int) -> tuple[dict, int]:
    """Delete a playlist owned by the user."""
    with db_session(db_path) as conn:
        cur = conn.execute(
            "DELETE FROM Playlists WHERE id = ? AND user_id = ?",
            (playlist_id, user_id),
        )
        if cur.rowcount == 0:
            return {"error": "Playlist not found"}, 404
    return {"message": "Playlist deleted", "playlist_id": playlist_id}, 200


def add_track_to_playlist(
    db_path: str | Path | None, user_id: int, playlist_id: int, track_id: int
) -> tuple[dict, int]:
    """Add a track to a user's playlist."""
    with db_session(db_path) as conn:
        pl = conn.execute(
            "SELECT id FROM Playlists WHERE id = ? AND user_id = ?", (playlist_id, user_id)
        ).fetchone()
        if pl is None:
            return {"error": "Playlist not found"}, 404
        track = conn.execute("SELECT id FROM Tracks WHERE id = ?", (track_id,)).fetchone()
        if track is None:
            return {"error": "Track not found"}, 404

        max_pos = conn.execute(
            "SELECT COALESCE(MAX(position), -1) FROM PlaylistTracks WHERE playlist_id = ?",
            (playlist_id,),
        ).fetchone()[0]
        try:
            conn.execute(
                "INSERT INTO PlaylistTracks (playlist_id, track_id, position) VALUES (?, ?, ?)",
                (playlist_id, track_id, max_pos + 1),
            )
            conn.execute(
                "UPDATE Playlists SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (playlist_id,),
            )
        except sqlite3.IntegrityError:
            return {"error": "Track already in playlist"}, 409
    return {"message": "Track added to playlist", "playlist_id": playlist_id, "track_id": track_id}, 201


def remove_track_from_playlist(
    db_path: str | Path | None, user_id: int, playlist_id: int, track_id: int
) -> tuple[dict, int]:
    """Remove a track from a user's playlist."""
    with db_session(db_path) as conn:
        pl = conn.execute(
            "SELECT id FROM Playlists WHERE id = ? AND user_id = ?", (playlist_id, user_id)
        ).fetchone()
        if pl is None:
            return {"error": "Playlist not found"}, 404
        conn.execute(
            "DELETE FROM PlaylistTracks WHERE playlist_id = ? AND track_id = ?",
            (playlist_id, track_id),
        )
        conn.execute(
            "UPDATE Playlists SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (playlist_id,),
        )
    return {"message": "Track removed from playlist", "playlist_id": playlist_id, "track_id": track_id}, 200


def record_listening_event(
    db_path: str | Path | None,
    user_id: int,
    track_id: int,
    play_duration_sec: int = 180,
    completed: bool = True,
) -> tuple[dict, int]:
    """Record a listening event in ListeningHistory."""
    with db_session(db_path) as conn:
        track = conn.execute("SELECT id, title, artist FROM Tracks WHERE id = ?", (track_id,)).fetchone()
        if track is None:
            return {"error": "Track not found"}, 404
        cur = conn.execute(
            """
            INSERT INTO ListeningHistory (user_id, track_id, play_duration_sec, completed)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, track_id, max(0, int(play_duration_sec)), 1 if completed else 0),
        )
        event_id = cur.lastrowid
    return {
        "event_id": event_id,
        "track_id": track_id,
        "title": track["title"],
        "artist": track["artist"],
    }, 201


def get_listening_history(db_path: str | Path | None, user_id: int, limit: int = 30) -> list[dict]:
    """Return user's recently played tracks with timestamps."""
    with db_session(db_path) as conn:
        rows = conn.execute(
            """
            SELECT lh.id AS event_id, lh.played_at, lh.play_duration_sec, lh.completed, t.*
            FROM ListeningHistory lh
            JOIN Tracks t ON t.id = lh.track_id
            WHERE lh.user_id = ?
            ORDER BY lh.played_at DESC, lh.id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["played_at"] = str(d["played_at"])
        result.append(d)
    return result
