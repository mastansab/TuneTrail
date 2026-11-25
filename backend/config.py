"""Application configuration for TuneTrail backend."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "tunetrail-dev-secret-key-2026")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "database" / "tunetrail.db"))
    HYBRID_ALPHA = float(os.environ.get("HYBRID_ALPHA", "0.6"))
    CORS_ORIGINS = [
        o.strip()
        for o in os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if o.strip()
    ]
    TOKEN_EXPIRY_SECONDS = int(os.environ.get("TOKEN_EXPIRY_SECONDS", "86400"))
    TESTING = False
