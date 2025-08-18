#!/usr/bin/env python3
"""
Reusable query execution context manager.

- Manages connection + execution.
- Returns fetched results from __enter__.
- Commits on success; rolls back on exception.
- Includes schema creation + seed before demo run.
"""

import sqlite3
from typing import Iterable, Tuple


class ExecuteQuery:
    """Context manager for executing queries with params"""

    def __init__(self, query: str, params: Iterable | Tuple = (), db_name: str = "my_database.db"):
        self.db_name = db_name
        self.query = query
        self.params = tuple(params) if params else ()
        self.conn: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None
        self.result = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        self.result = self.cursor.fetchall()
        return self.result

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.conn:
            return False
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()
        return False


def _ensure_schema_and_seed(db_name: str = "my_database.db") -> None:
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
            """
        )
        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO users (name, age) VALUES (?, ?)",
                [
                    ("Ada", 22),
                    ("Bayo", 28),
                    ("Chioma", 35),
                    ("Dare", 41),
                    ("Efe", 55),
                ],
            )
        conn.commit()


if __name__ == "__main__":
    _ensure_schema_and_seed("my_database.db")
    query = "SELECT * FROM users WHERE age > ?;"
    with ExecuteQuery(query, (25,), db_name="my_database.db") as result:
        print(result)
