"""SQLite database connection and initialization utilities."""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
DEFAULT_DB_PATH = Path(__file__).resolve().parent / "tunetrail.db"


def get_db_path(db_path: str | Path | None = None) -> Path:
    """Resolve the SQLite database file path."""
    if db_path is not None:
        return Path(db_path)
    env_path = os.environ.get("DATABASE_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_DB_PATH


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Create a configured SQLite connection with foreign keys enabled."""
    resolved = get_db_path(db_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(resolved))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def db_session(db_path: str | Path | None = None) -> Iterator[sqlite3.Connection]:
    """Provide a transactional SQLite connection context manager."""
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: str | Path | None = None) -> None:
    """Initialize database tables and indexes from schema.sql."""
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with db_session(db_path) as conn:
        conn.executescript(schema_sql)
