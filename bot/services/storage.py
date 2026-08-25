from __future__ import annotations

import time
from dataclasses import dataclass

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    lang TEXT NOT NULL DEFAULT 'ru',
    created_at INTEGER NOT NULL,
    last_seen_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS processed_videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    created_at INTEGER NOT NULL,
    ops_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS required_channels (
    lang TEXT PRIMARY KEY,
    channel TEXT NOT NULL
);
"""


@dataclass
class UserRecord:
    user_id: int
    username: str | None
    lang: str


class Storage:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._db = await aiosqlite.connect(self._db_path)
        await self._db.executescript(SCHEMA)
        await self._db.commit()

    async def close(self) -> None:
        if self._db is not None:
            await self._db.close()

    @property
    def db(self) -> aiosqlite.Connection:
        assert self._db is not None, "Storage.connect() was not called"
        return self._db

    async def get_user(self, user_id: int) -> UserRecord | None:
        cursor = await self.db.execute(
            "SELECT user_id, username, lang FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return UserRecord(user_id=row[0], username=row[1], lang=row[2])

    async def upsert_user(self, user_id: int, username: str | None, lang: str | None = None) -> None:
        now = int(time.time())
        existing = await self.get_user(user_id)
        if existing is None:
            await self.db.execute(
                "INSERT INTO users (user_id, username, lang, created_at, last_seen_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, username, lang or "ru", now, now),
            )
        else:
            new_lang = lang or existing.lang
            await self.db.execute(
                "UPDATE users SET username = ?, lang = ?, last_seen_at = ? WHERE user_id = ?",
                (username, new_lang, now, user_id),
            )
        await self.db.commit()

    async def set_lang(self, user_id: int, lang: str) -> None:
        await self.db.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))
        await self.db.commit()

    async def log_processed_video(self, user_id: int, ops_count: int) -> None:
        await self.db.execute(
            "INSERT INTO processed_videos (user_id, created_at, ops_count) VALUES (?, ?, ?)",
            (user_id, int(time.time()), ops_count),
        )
        await self.db.commit()

    async def set_required_channel(self, lang: str, channel: str | None) -> None:
        if channel is None:
            await self.db.execute("DELETE FROM required_channels WHERE lang = ?", (lang,))
        else:
            await self.db.execute(
                "INSERT INTO required_channels (lang, channel) VALUES (?, ?) "
                "ON CONFLICT(lang) DO UPDATE SET channel = excluded.channel",
                (lang, channel),
            )
        await self.db.commit()

    async def get_required_channel(self, lang: str) -> str | None:
        cursor = await self.db.execute(
            "SELECT channel FROM required_channels WHERE lang = ?", (lang,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None

    async def get_required_channels(self) -> dict[str, str]:
        cursor = await self.db.execute("SELECT lang, channel FROM required_channels")
        rows = await cursor.fetchall()
        return {lang: channel for lang, channel in rows}

    async def all_user_ids(self) -> list[int]:
        cursor = await self.db.execute("SELECT user_id FROM users")
        rows = await cursor.fetchall()
        return [r[0] for r in rows]

    async def stats(self) -> dict[str, int]:
        cursor = await self.db.execute("SELECT COUNT(*) FROM users")
        (users_total,) = await cursor.fetchone()

        cursor = await self.db.execute("SELECT COUNT(*) FROM processed_videos")
        (videos_total,) = await cursor.fetchone()

        day_ago = int(time.time()) - 86400
        cursor = await self.db.execute(
            "SELECT COUNT(*) FROM processed_videos WHERE created_at >= ?", (day_ago,)
        )
        (videos_24h,) = await cursor.fetchone()

        cursor = await self.db.execute(
            "SELECT COUNT(*) FROM users WHERE created_at >= ?", (day_ago,)
        )
        (new_users_24h,) = await cursor.fetchone()

        return {
            "users_total": users_total,
            "videos_total": videos_total,
            "videos_24h": videos_24h,
            "new_users_24h": new_users_24h,
        }
