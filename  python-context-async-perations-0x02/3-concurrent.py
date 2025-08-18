#!/usr/bin/env python3
"""
Concurrent async queries using aiosqlite and asyncio.gather.

- Creates schema and seeds data if empty.
- Fetches all users and users older than 40 concurrently.
"""

import asyncio
import aiosqlite


async def async_init_db(db_name: str = "my_database.db") -> None:
    async with aiosqlite.connect(db_name) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
            """
        )
        # Check if empty
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            (count,) = await cursor.fetchone()
        if count == 0:
            await db.executemany(
                "INSERT INTO users (name, age) VALUES (?, ?)",
                [
                    ("Ada", 22),
                    ("Bayo", 28),
                    ("Chioma", 35),
                    ("Dare", 41),
                    ("Efe", 55),
                ],
            )
        await db.commit()


async def async_fetch_users(db_name: str = "my_database.db"):
    async with aiosqlite.connect(db_name) as db:
        async with db.execute("SELECT * FROM users;") as cursor:
            return await cursor.fetchall()


async def async_fetch_older_users(db_name: str = "my_database.db"):
    async with aiosqlite.connect(db_name) as db:
        async with db.execute("SELECT * FROM users WHERE age > 40;") as cursor:
            return await cursor.fetchall()


async def fetch_concurrently():
    # Ensure DB is ready
    await async_init_db("my_database.db")

    users, older_users = await asyncio.gather(
        async_fetch_users("my_database.db"),
        async_fetch_older_users("my_database.db")
    )
