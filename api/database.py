"""SQLite persistence for the leaderboard."""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

DB_PATH = Path(os.getenv("SNAKE_DB_PATH", "snake_scores.db"))


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connection() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player TEXT NOT NULL,
                score INTEGER NOT NULL CHECK(score >= 0),
                level INTEGER NOT NULL CHECK(level >= 1),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )


def add_score(player: str, score: int, level: int) -> dict:
    with connection() as conn:
        cur = conn.execute(
            "INSERT INTO scores(player, score, level) VALUES (?, ?, ?)",
            (player, score, level),
        )
        row = conn.execute("SELECT * FROM scores WHERE id = ?", (cur.lastrowid,)).fetchone()
        return dict(row)


def leaderboard(limit: int = 10) -> list[dict]:
    with connection() as conn:
        rows = conn.execute(
            "SELECT player, score, level, created_at FROM scores "
            "ORDER BY score DESC, created_at ASC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]


def stats() -> dict:
    with connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS games, COALESCE(MAX(score), 0) AS best, "
            "COALESCE(AVG(score), 0) AS average FROM scores"
        ).fetchone()
        return {"games": row["games"], "best": row["best"], "average": round(row["average"], 2)}
