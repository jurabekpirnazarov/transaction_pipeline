from __future__ import annotations

import sqlite3
from typing import Iterable, Mapping, Tuple


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    transaction_date TEXT NOT NULL, -- ISO YYYY-MM-DD
    amount REAL NOT NULL,
    category TEXT
);
CREATE INDEX IF NOT EXISTS idx_transactions_user_date
    ON transactions(user_id, transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_category
    ON transactions(category);
"""


def init_db(db_path: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()


def insert_transactions(db_path: str, rows: Iterable[Mapping[str, object]]) -> Tuple[int, int]:
    """
    Insert rows into the DB.
    Returns (inserted_count, skipped_count) where skipped are conflicts on primary key.
    """
    inserted = 0
    skipped = 0
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        for r in rows:
            try:
                cur.execute(
                    "INSERT OR IGNORE INTO transactions(transaction_id, user_id, transaction_date, amount, category) "
                    "VALUES(?,?,?,?,?)",
                    (
                        r["transaction_id"],
                        int(r["user_id"]),
                        str(r["transaction_date"]),
                        float(r["amount"]),
                        r.get("category"),
                    ),
                )
                if cur.rowcount == 0:
                    skipped += 1
                else:
                    inserted += 1
            except Exception:
                # Treat as skip if a row fails due to type mismatch, etc.
                skipped += 1
        conn.commit()
    return inserted, skipped


def summary(db_path: str):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM transactions")
        total_tx = cur.fetchone()[0]

        cur.execute(
            "SELECT COALESCE(category, 'UNCATEGORIZED') as category, COUNT(*), "
            "ROUND(SUM(amount), 2), ROUND(AVG(amount), 2) "
            "FROM transactions GROUP BY category ORDER BY SUM(amount) DESC NULLS LAST"
        )
        per_category = [
            {"category": row[0], "count": row[1], "total": row[2], "average": row[3]}
            for row in cur.fetchall()
        ]

        cur.execute("SELECT MIN(transaction_date), MAX(transaction_date) FROM transactions")
        min_date, max_date = cur.fetchone()

    return {
        "total_transactions": total_tx,
        "per_category": per_category,
        "date_range": {"start": min_date, "end": max_date},
    }
