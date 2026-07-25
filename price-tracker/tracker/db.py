"""SQLite storage for tracked products, price history, and sent alerts."""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "tracker.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    name TEXT,
    currency TEXT,
    target_price REAL,
    drop_pct REAL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    price REAL NOT NULL,
    checked_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    rule TEXT NOT NULL,
    price REAL NOT NULL,
    sent_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_price_history_product ON price_history(product_id, checked_at);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def add_product(url: str, name: str | None, currency: str | None,
                 target_price: float | None, drop_pct: float | None) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO products (url, name, currency, target_price, drop_pct, active, created_at) "
            "VALUES (?, ?, ?, ?, ?, 1, ?)",
            (url, name, currency, target_price, drop_pct, now_iso()),
        )
        return cur.lastrowid


def get_product_by_url(url: str) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM products WHERE url = ?", (url,)).fetchone()


def get_product(product_id: int) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()


def list_products(active_only: bool = True) -> list[sqlite3.Row]:
    with get_conn() as conn:
        if active_only:
            return conn.execute("SELECT * FROM products WHERE active = 1 ORDER BY id").fetchall()
        return conn.execute("SELECT * FROM products ORDER BY id").fetchall()


def remove_product(product_id: int):
    with get_conn() as conn:
        conn.execute("UPDATE products SET active = 0 WHERE id = ?", (product_id,))


def record_price(product_id: int, price: float, checked_at: str | None = None) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO price_history (product_id, price, checked_at) VALUES (?, ?, ?)",
            (product_id, price, checked_at or now_iso()),
        )
        return cur.lastrowid


def get_price_history(product_id: int, since: str | None = None) -> list[sqlite3.Row]:
    with get_conn() as conn:
        if since:
            return conn.execute(
                "SELECT * FROM price_history WHERE product_id = ? AND checked_at >= ? ORDER BY checked_at",
                (product_id, since),
            ).fetchall()
        return conn.execute(
            "SELECT * FROM price_history WHERE product_id = ? ORDER BY checked_at",
            (product_id,),
        ).fetchall()


def get_latest_price(product_id: int) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM price_history WHERE product_id = ? ORDER BY checked_at DESC LIMIT 1",
            (product_id,),
        ).fetchone()


def record_alert(product_id: int, rule: str, price: float):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO alerts (product_id, rule, price, sent_at) VALUES (?, ?, ?, ?)",
            (product_id, rule, price, now_iso()),
        )


def get_last_alert(product_id: int, rule: str) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM alerts WHERE product_id = ? AND rule = ? ORDER BY sent_at DESC LIMIT 1",
            (product_id, rule),
        ).fetchone()
