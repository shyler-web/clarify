import os
import sqlite3


def _db_path() -> str:
    return os.environ.get("PAYDOWN_DB", "paydown.db")


def _connect():
    conn = sqlite3.connect(_db_path())
    conn.execute("CREATE TABLE IF NOT EXISTS intents(file_path TEXT PRIMARY KEY, note TEXT)")
    conn.commit()
    return conn


def save_intent(file_path: str, note: str) -> None:
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO intents(file_path, note) VALUES(?, ?) "
            "ON CONFLICT(file_path) DO UPDATE SET note = excluded.note",
            (file_path, note),
        )
        conn.commit()
    finally:
        conn.close()


def load_intent(file_path: str) -> str | None:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT note FROM intents WHERE file_path = ?", (file_path,)
        ).fetchone()
        return row[0] if row else None
    finally:
        conn.close()