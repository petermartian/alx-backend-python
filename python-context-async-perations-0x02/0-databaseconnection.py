#!/usr/bin/env python3
"""
Custom context manager for handling SQLite connections.

- Ensures connection open/close.
- Commits on success; rolls back on exception.
- Creates 'users' table and seeds sample data if empty before SELECT.
"""

import sqlite3


class DatabaseConnection:
    """Context manager to handle DB connection automatically"""

    def __init__(self, db_name: str = "my_database.db"):
        self.db_name = db_name
        self.conn: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None

    def __enter__(self) -> sqlite3.Cursor:
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.conn:
            return False
        if exc_type is None:
            self.conn.commit()
        else:
            # Roll back on any exception
            self.conn.rollback()
        self.conn.close()
        # returning False propagates exceptions (good for debugging)
        return False


def _ensure_schema_and_seed(db_name: str = "my_database.db") -> None:
    with DatabaseConnection(db_name) as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
            """
        )
        # Check if empty, then seed
        cur.execute("SELECT COUNT(*) FROM users")
        count = cur.fetchone()[0]
        if count == 0:
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


if __name__ == "__main__":
    _ensure_schema_and_seed("my_database.db")
    with DatabaseConnection("my_database.db") as cursor:
        cursor.execute("SELECT * FROM users;")
        results = cursor.fetchall()
        print(results)
