MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "geographic_db"
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import os

"""
Helpers to read DB-related environment variables in a typed way.

These are convenience utilities only — existing code paths are unchanged.
Nothing here opens network connections or has import-time side effects.
"""

@dataclass(frozen=True)
class DBSettings:
    database_url: Optional[str] = None      # e.g., postgres://..., mongodb://..., sqlite:///:memory:
    mongo_uri: Optional[str] = None         # alternate single-URL var some teams prefer
    host: Optional[str] = None
    port: Optional[int] = None
    name: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None

def load_db_settings() -> DBSettings:
    """Load DB settings from environment variables (all optional)."""
    def _int(val: Optional[str]) -> Optional[int]:
        try:
            return int(val) if val is not None and val != "" else None
        except ValueError:
            return None

    return DBSettings(
        database_url=os.getenv("DATABASE_URL"),
        mongo_uri=os.getenv("MONGO_URI"),
        host=os.getenv("DB_HOST"),
        port=_int(os.getenv("DB_PORT")),
        name=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

def compose_url(s: DBSettings) -> Optional[str]:
    """
    Return a single connection URL if one is readily available.
    Prefers DATABASE_URL, then MONGO_URI. If neither is set, tries to compose
    a simple mongodb:// URL from split parts when host+name are present.
    """
    if s.database_url:
        return s.database_url
    if s.mongo_uri:
        return s.mongo_uri
    if s.host and s.name:
        auth = ""
        if s.user:
            # redact password in composed URL if not provided
            auth = f"{s.user}:{s.password or ''}@"
        port = f":{s.port}" if s.port else ""
        return f"mongodb://{auth}{s.host}{port}/{s.name}"
    return None
