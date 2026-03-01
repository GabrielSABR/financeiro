"""SQLite persistence for expenses and budgets."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from pathlib import Path

DB_PATH = Path("data/financeiro.db")


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                amount TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                phone TEXT PRIMARY KEY,
                amount TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


@contextmanager
def _connect():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def add_expense(phone: str, description: str, category: str, amount: Decimal) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO expenses(phone, description, category, amount, created_at) VALUES (?, ?, ?, ?, ?)",
            (phone, description, category, str(amount), datetime.utcnow().isoformat()),
        )


def get_month_total(phone: str, month_prefix: str) -> Decimal:
    with _connect() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(CAST(amount AS REAL)),0) FROM expenses WHERE phone=? AND created_at LIKE ?",
            (phone, f"{month_prefix}%"),
        ).fetchone()
    return Decimal(str(row[0] or 0))


def set_budget(phone: str, amount: Decimal) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO budgets(phone, amount, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(phone) DO UPDATE SET amount=excluded.amount, updated_at=excluded.updated_at
            """,
            (phone, str(amount), datetime.utcnow().isoformat()),
        )


def get_budget(phone: str) -> Decimal | None:
    with _connect() as conn:
        row = conn.execute("SELECT amount FROM budgets WHERE phone=?", (phone,)).fetchone()
    return Decimal(row[0]) if row else None
