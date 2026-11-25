-- TuneTrail SQLite Database Schema
-- Enforces referential integrity, domain validation, and indexing.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE CHECK(length(trim(username)) >= 3),
    email TEXT NOT NULL UNIQUE CHECK(instr(email, '@') > 1),
    password_hash TEXT NOT NULL,
    display_name TEXT NOT NULL CHECK(length(trim(display_name)) >= 1),
    role TEXT NOT NULL DEFAULT 'listener' CHECK(role IN ('listener', 'admin')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(trim(title)) >= 1),
    artist TEXT NOT NULL CHECK(length(trim(artist)) >= 1),
    album TEXT NOT NULL DEFAULT 'Single',
    genre TEXT NOT NULL CHECK(length(trim(genre)) >= 1),
    release_year INTEGER NOT NULL CHECK(release_year BETWEEN 1950 AND 2030),
    duration_sec INTEGER NOT NULL CHECK(duration_sec > 0),
    tempo REAL NOT NULL CHECK(tempo > 0),
    energy REAL NOT NULL CHECK(energy BETWEEN 0.0 AND 1.0),
    danceability REAL NOT NULL CHECK(danceability BETWEEN 0.0 AND 1.0),
    valence REAL NOT NULL CHECK(valence BETWEEN 0.0 AND 1.0),
    acousticness REAL NOT NULL CHECK(acousticness BETWEEN 0.0 AND 1.0),
    popularity INTEGER NOT NULL DEFAULT 50 CHECK(popularity BETWEEN 0 AND 100),
    cover_color TEXT NOT NULL DEFAULT '#7c3aed',
    tags TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS Playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL CHECK(length(trim(name)) >= 1),
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS PlaylistTracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    playlist_id INTEGER NOT NULL,
    track_id INTEGER NOT NULL,
    position INTEGER NOT NULL DEFAULT 0,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(playlist_id, track_id),
    FOREIGN KEY (playlist_id) REFERENCES Playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (track_id) REFERENCES Tracks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ListeningHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    track_id INTEGER NOT NULL,
    played_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    play_duration_sec INTEGER NOT NULL DEFAULT 0 CHECK(play_duration_sec >= 0),
    completed INTEGER NOT NULL DEFAULT 1 CHECK(completed IN (0, 1)),
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (track_id) REFERENCES Tracks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS UserPreferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    preferred_genres TEXT NOT NULL DEFAULT '[]',
    preferred_artists TEXT NOT NULL DEFAULT '[]',
    hybrid_alpha REAL NOT NULL DEFAULT 0.6 CHECK(hybrid_alpha BETWEEN 0.0 AND 1.0),
    avoid_recent_count INTEGER NOT NULL DEFAULT 5 CHECK(avoid_recent_count >= 0),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Favourites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    track_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, track_id),
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (track_id) REFERENCES Tracks(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tracks_genre ON Tracks(genre);
CREATE INDEX IF NOT EXISTS idx_tracks_artist ON Tracks(artist);
CREATE INDEX IF NOT EXISTS idx_history_user_time ON ListeningHistory(user_id, played_at DESC);
CREATE INDEX IF NOT EXISTS idx_history_track ON ListeningHistory(track_id);
CREATE INDEX IF NOT EXISTS idx_playlists_user ON Playlists(user_id);
CREATE INDEX IF NOT EXISTS idx_favourites_user ON Favourites(user_id);
