"""Database seeder for TuneTrail synthetic music dataset and user interactions."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from werkzeug.security import generate_password_hash

from database.db import db_session, init_db

DATASET_PATH = Path(__file__).resolve().parent.parent / "datasets" / "tracks.json"

# 12 active users across 3 taste clusters + 1 cold-start user ('newbie')
SEED_USERS = [
    ("demo", "demo@tunetrail.ai", "Demo@1234", "Alex Mercer", "listener", ["Synthwave", "Electronic"], ["Midnight Pulse", "Aether & Flux"]),
    ("alex_s", "alex.s@tunetrail.ai", "Pass@1234", "Alex Silva", "listener", ["Synthwave", "Electronic"], ["Vespera", "Nyxon"]),
    ("nova_v", "nova.v@tunetrail.ai", "Pass@1234", "Nova Vance", "listener", ["Synthwave", "Electronic"], ["Midnight Pulse", "Lumenwave"]),
    ("kairo_m", "kairo.m@tunetrail.ai", "Pass@1234", "Kairo Mori", "listener", ["Synthwave", "Electronic"], ["Kova & The Grid", "Kyra V"]),
    ("maya_l", "maya.l@tunetrail.ai", "Pass@1234", "Maya Lin", "listener", ["Lo-Fi", "Ambient"], ["Kumo Beats", "Halcyon Drift"]),
    ("zen_r", "zen.r@tunetrail.ai", "Pass@1234", "Zen Rao", "listener", ["Lo-Fi", "Ambient", "Jazz Fusion"], ["Mori Tape", "Tundra Echo"]),
    ("claire_j", "claire.j@tunetrail.ai", "Pass@1234", "Claire Jenkins", "listener", ["Lo-Fi", "Jazz Fusion"], ["Sora & Pine", "Julian Vance Quartet"]),
    ("omar_f", "omar.f@tunetrail.ai", "Pass@1234", "Omar Farooq", "listener", ["Ambient", "Jazz Fusion"], ["Halcyon Drift", "Nadia Okafor"]),
    ("liam_k", "liam.k@tunetrail.ai", "Pass@1234", "Liam Karter", "listener", ["Indie Pop", "Alt Rock"], ["Sunlit Youth", "Ironclad Echo"]),
    ("zoe_p", "zoe.p@tunetrail.ai", "Pass@1234", "Zoe Patel", "listener", ["Indie Pop", "R&B Soul"], ["Clara & The Echoes", "Selena Monroe"]),
    ("ryan_t", "ryan.t@tunetrail.ai", "Pass@1234", "Ryan Torres", "listener", ["Alt Rock", "Indie Pop"], ["Silverline", "Juneberry"]),
    ("priya_n", "priya.n@tunetrail.ai", "Pass@1234", "Priya Nair", "listener", ["R&B Soul", "Indie Pop"], ["Selena Monroe", "Devon Cruz"]),
    ("newbie", "newbie@tunetrail.ai", "Pass@1234", "Sam Rivera", "listener", ["Synthwave", "Lo-Fi"], ["Midnight Pulse"]),
]


def seed_database(db_path: str | Path | None = None, force: bool = False) -> dict:
    """Initialize schema and populate synthetic tracks, users, histories, and playlists."""
    init_db(db_path)
    tracks_data = json.loads(DATASET_PATH.read_text(encoding="utf-8"))

    with db_session(db_path) as conn:
        existing_tracks = conn.execute("SELECT COUNT(*) FROM Tracks").fetchone()[0]
        if existing_tracks > 0 and not force:
            return {"status": "already_seeded", "tracks": existing_tracks}

        if force:
            for table in ("PlaylistTracks", "Playlists", "ListeningHistory", "Favourites", "UserPreferences", "Tracks", "Users"):
                conn.execute(f"DELETE FROM {table}")

        # 1. Insert Tracks
        track_ids_by_genre: dict[str, list[int]] = {}
        for t in tracks_data:
            cur = conn.execute(
                """
                INSERT INTO Tracks (
                    title, artist, album, genre, release_year, duration_sec,
                    tempo, energy, danceability, valence, acousticness, popularity, cover_color, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    t["title"], t["artist"], t["album"], t["genre"], t["release_year"],
                    t["duration_sec"], t["tempo"], t["energy"], t["danceability"],
                    t["valence"], t["acousticness"], t["popularity"], t["cover_color"], t["tags"],
                ),
            )
            track_id = cur.lastrowid
            track_ids_by_genre.setdefault(t["genre"], []).append(track_id)

        # 2. Insert Users & Preferences
        user_ids: dict[str, int] = {}
        for username, email, password, display_name, role, pref_genres, pref_artists in SEED_USERS:
            cur = conn.execute(
                """
                INSERT INTO Users (username, email, password_hash, display_name, role)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, email, generate_password_hash(password), display_name, role),
            )
            uid = cur.lastrowid
            user_ids[username] = uid
            conn.execute(
                """
                INSERT INTO UserPreferences (user_id, preferred_genres, preferred_artists, hybrid_alpha, avoid_recent_count)
                VALUES (?, ?, ?, ?, ?)
                """,
                (uid, json.dumps(pref_genres), json.dumps(pref_artists), 0.6, 5),
            )

        # 3. Cluster-coherent listening histories (so Collaborative Filtering + evaluation are meaningful)
        now = datetime.now()
        cluster_tracks = {
            "synth_elec": track_ids_by_genre["Synthwave"] + track_ids_by_genre["Electronic"],
            "lofi_amb_jazz": track_ids_by_genre["Lo-Fi"] + track_ids_by_genre["Ambient"] + track_ids_by_genre["Jazz Fusion"],
            "indie_rock_rnb": track_ids_by_genre["Indie Pop"] + track_ids_by_genre["Alt Rock"] + track_ids_by_genre["R&B Soul"],
        }

        user_cluster_map = {
            "demo": ("synth_elec", [0, 1, 2, 3, 4, 8, 9, 10, 12, 14]),
            "alex_s": ("synth_elec", [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 13, 15]),
            "nova_v": ("synth_elec", [0, 1, 3, 4, 6, 7, 8, 9, 12, 14, 15]),
            "kairo_m": ("synth_elec", [1, 2, 4, 5, 6, 8, 10, 11, 13, 14, 15]),
            "maya_l": ("lofi_amb_jazz", [0, 1, 2, 3, 4, 7, 8, 9, 10, 13]),
            "zen_r": ("lofi_amb_jazz", [0, 1, 2, 4, 5, 7, 8, 10, 11, 14, 15]),
            "claire_j": ("lofi_amb_jazz", [0, 2, 3, 4, 6, 13, 14, 15, 16, 17]),
            "omar_f": ("lofi_amb_jazz", [1, 7, 8, 9, 11, 12, 13, 14, 17, 18]),
            "liam_k": ("indie_rock_rnb", [0, 1, 2, 3, 7, 8, 9, 10, 11]),
            "zoe_p": ("indie_rock_rnb", [0, 1, 2, 3, 4, 5, 13, 14, 15, 16]),
            "ryan_t": ("indie_rock_rnb", [0, 2, 4, 7, 8, 9, 10, 11, 12]),
            "priya_n": ("indie_rock_rnb", [1, 3, 5, 6, 13, 14, 15, 16, 17, 18]),
        }

        history_count = 0
        for username, (cluster_key, indices) in user_cluster_map.items():
            uid = user_ids[username]
            pool = cluster_tracks[cluster_key]
            for step, idx in enumerate(indices):
                tid = pool[idx % len(pool)]
                played_at = (now - timedelta(days=(len(indices) - step) % 7, hours=step * 2)).strftime("%Y-%m-%d %H:%M:%S")
                conn.execute(
                    """
                    INSERT INTO ListeningHistory (user_id, track_id, played_at, play_duration_sec, completed)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (uid, tid, played_at, 195, 1),
                )
                history_count += 1
                if step < 4:
                    conn.execute(
                        "INSERT OR IGNORE INTO Favourites (user_id, track_id) VALUES (?, ?)",
                        (uid, tid),
                    )

        # 4. Seed Playlists for demo user
        demo_uid = user_ids["demo"]
        p1 = conn.execute(
            "INSERT INTO Playlists (user_id, name, description) VALUES (?, ?, ?)",
            (demo_uid, "Midnight Drive", "High-energy synthwave and electronic grooves for late-night coding."),
        ).lastrowid
        for pos, tid in enumerate(cluster_tracks["synth_elec"][:5]):
            conn.execute(
                "INSERT INTO PlaylistTracks (playlist_id, track_id, position) VALUES (?, ?, ?)",
                (p1, tid, pos),
            )

        p2 = conn.execute(
            "INSERT INTO Playlists (user_id, name, description) VALUES (?, ?, ?)",
            (demo_uid, "Deep Focus Lo-Fi", "Calm instrumental beats for study sessions."),
        ).lastrowid
        for pos, tid in enumerate(track_ids_by_genre["Lo-Fi"][:4]):
            conn.execute(
                "INSERT INTO PlaylistTracks (playlist_id, track_id, position) VALUES (?, ?, ?)",
                (p2, tid, pos),
            )

        return {
            "status": "seeded",
            "tracks": len(tracks_data),
            "users": len(SEED_USERS),
            "history_events": history_count,
        }


if __name__ == "__main__":
    result = seed_database(force=True)
    print(f"Database initialized: {result}")
