from __future__ import annotations

import asyncio
import logging
import sys
import time
from pathlib import Path

import aiohttp

from bot.config import config

logger = logging.getLogger(__name__)

_MAX_COOKIE_FILE_BYTES = 100_000
# "Me at the zoo" — the first video ever uploaded to YouTube; short, always public, ideal test target.
_TEST_VIDEO_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"


class CookieManager:
    """Keeps a validated YouTube cookies.txt on disk, rotating through backup URLs on failure."""

    def __init__(self, work_dir: Path) -> None:
        self._active_path = work_dir / "cookies_active.txt"
        self._checked_at = 0.0
        self._lock = asyncio.Lock()

    async def get_path(self, http_session: aiohttp.ClientSession) -> Path | None:
        if config.cookies_file:
            return Path(config.cookies_file)
        if not config.cookie_urls:
            return None

        async with self._lock:
            fresh = time.time() - self._checked_at < config.cookie_revalidate_minutes * 60
            if fresh and self._active_path.exists():
                return self._active_path

            for url in config.cookie_urls:
                if await self._try_source(http_session, url):
                    self._checked_at = time.time()
                    return self._active_path
                logger.warning("cookie source failed validation: %s", url)

            if self._active_path.exists():
                logger.warning("all cookie sources failed validation, reusing last known-good cookies")
                return self._active_path

            logger.error("no working YouTube cookies found among %d configured source(s)", len(config.cookie_urls))
            return None

    async def _try_source(self, http_session: aiohttp.ClientSession, url: str) -> bool:
        try:
            async with http_session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    return False
                data = await resp.read()
        except (aiohttp.ClientError, asyncio.TimeoutError):
            logger.warning("failed to fetch cookies from %s", url)
            return False

        if not data or len(data) > _MAX_COOKIE_FILE_BYTES:
            return False
        text = data.decode(errors="ignore")
        if "\t" not in text:  # not a Netscape-format cookies file
            return False

        candidate_path = self._active_path.with_suffix(".candidate")
        candidate_path.parent.mkdir(parents=True, exist_ok=True)
        candidate_path.write_bytes(data)

        if await self._validate(candidate_path):
            candidate_path.replace(self._active_path)
            return True

        candidate_path.unlink(missing_ok=True)
        return False

    @staticmethod
    async def _validate(path: Path) -> bool:
        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "yt_dlp",
            "--cookies",
            str(path),
            "--simulate",
            "--skip-download",
            "--no-warnings",
            _TEST_VIDEO_URL,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.warning("cookie validation failed: %s", stderr.decode(errors="ignore")[-500:])
        return proc.returncode == 0
