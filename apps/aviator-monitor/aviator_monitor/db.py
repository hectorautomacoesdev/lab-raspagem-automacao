"""Armazenamento SQLite dos resultados do Aviator."""
from __future__ import annotations

import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

from .config import CONFIG

SCHEMA = """
CREATE TABLE IF NOT EXISTS rounds (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_epoch    REAL NOT NULL,
    ts_iso      TEXT NOT NULL,
    multiplier  REAL NOT NULL,
    house       TEXT NOT NULL,
    mode        TEXT NOT NULL DEFAULT 'demo',
    source      TEXT NOT NULL DEFAULT 'strip',
    raw_text    TEXT
);
CREATE INDEX IF NOT EXISTS idx_rounds_ts ON rounds(ts_epoch);
"""


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path or CONFIG.db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def insert_round(conn, multiplier, house=None, mode=None,
                 source="strip", raw_text=None, ts=None) -> int:
    ts = time.time() if ts is None else ts
    iso = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO rounds (ts_epoch, ts_iso, multiplier, house, mode, source, raw_text) "
        "VALUES (?,?,?,?,?,?,?)",
        (ts, iso, float(multiplier), house or CONFIG.house,
         mode or CONFIG.mode, source, raw_text),
    )
    conn.commit()
    return cur.lastrowid


def insert_many(conn, multipliers, **kw) -> list[int]:
    return [insert_round(conn, m, **kw) for m in multipliers]


def recent(conn, n=20):
    """Últimos n rounds, do mais novo para o mais antigo."""
    return conn.execute(
        "SELECT * FROM rounds ORDER BY id DESC LIMIT ?", (n,)
    ).fetchall()


def count(conn) -> int:
    return conn.execute("SELECT COUNT(*) AS c FROM rounds").fetchone()["c"]


def all_multipliers(conn, house=None) -> list[float]:
    """Todos os multiplicadores em ordem cronológica (mais antigo primeiro)."""
    if house:
        rows = conn.execute(
            "SELECT multiplier FROM rounds WHERE house=? ORDER BY id", (house,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT multiplier FROM rounds ORDER BY id").fetchall()
    return [r["multiplier"] for r in rows]


def last_multiplier(conn):
    row = conn.execute(
        "SELECT multiplier FROM rounds ORDER BY id DESC LIMIT 1"
    ).fetchone()
    return row["multiplier"] if row else None
