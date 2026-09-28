"""SQLite の接続と、原子的なトランザクション。"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from .config import JST

SCHEMA = Path(__file__).with_name("schema.sql")


def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, isolation_level=None, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 15000")
    if path != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))


@contextmanager
def tx(conn: sqlite3.Connection):
    """書き込みロックを先に取る（BEGIN IMMEDIATE）。並列のジョブが同じ残額を見て、両方が通ることを防ぐ。"""
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")


def now_iso(now: datetime | None = None) -> str:
    return (now or datetime.now(JST)).astimezone(JST).isoformat(timespec="seconds")


def audit(conn: sqlite3.Connection, actor: str, action: str, outcome: str, detail: str = "", now: datetime | None = None) -> None:
    conn.execute(
        "INSERT INTO audit (at, actor, action, outcome, detail) VALUES (?,?,?,?,?)",
        (now_iso(now), actor, action, outcome, detail),
    )
