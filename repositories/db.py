"""
repositories/db.py
SQLite connection helper.

Single source of truth for connection settings:
    - foreign_keys = ON
    - row_factory  = sqlite3.Row (so columns are addressable by name)
    - journal_mode = WAL (matches schema.sql PRAGMA)

Usage:
    from repositories.db import get_connection

    with get_connection() as conn:
        row = conn.execute("SELECT * FROM User_Profile WHERE id = 1").fetchone()
"""

import sqlite3
from pathlib import Path
from typing import Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "linkup.db"


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Return a configured SQLite connection.

    Caller is responsible for closing or using `with` block.
    """
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_db(db_path: Optional[Path] = None,
            schema_path: Optional[Path] = None,
            triggers_path: Optional[Path] = None,
            seed_path: Optional[Path] = None) -> None:
    """Initialize a fresh DB by running schema + triggers + seed scripts.

    Idempotent: schema.sql / triggers_and_indexes.sql use CREATE TABLE IF NOT EXISTS.
    Seed insertions use INSERT OR IGNORE.

    For v1 → v2 migration of an existing DB, run schema_v2.sql separately
    (NOT covered by this function).
    """
    repo_dir = Path(__file__).resolve().parent.parent
    schema_path   = Path(schema_path)   if schema_path   else repo_dir / "schema.sql"
    triggers_path = Path(triggers_path) if triggers_path else repo_dir / "triggers_and_indexes.sql"
    seed_path     = Path(seed_path)     if seed_path     else repo_dir / "seed_data.sql"

    with get_connection(db_path) as conn:
        for p in (schema_path, triggers_path, seed_path):
            if p.exists():
                conn.executescript(p.read_text(encoding="utf-8"))
        conn.commit()
