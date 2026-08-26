from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _parse_admin_ids(raw: str) -> set[int]:
    return {int(x) for x in raw.split(",") if x.strip().isdigit()}


@dataclass(frozen=True)
class Config:
    bot_token: str = field(default_factory=lambda: os.environ["BOT_TOKEN"])
    admin_ids: set[int] = field(default_factory=lambda: _parse_admin_ids(os.getenv("ADMIN_IDS", "")))
    db_path: str = field(default_factory=lambda: os.getenv("DB_PATH", "uniqvid.db"))
    work_dir: str = field(default_factory=lambda: os.getenv("WORK_DIR", "work"))
    max_video_mb: int = field(default_factory=lambda: int(os.getenv("MAX_VIDEO_MB", "50")))
    ffmpeg_bin: str = field(default_factory=lambda: os.getenv("FFMPEG_BIN", "ffmpeg"))
    ffprobe_bin: str = field(default_factory=lambda: os.getenv("FFPROBE_BIN", "ffprobe"))
    broadcast_delay_sec: float = field(default_factory=lambda: float(os.getenv("BROADCAST_DELAY_SEC", "0.05")))
    download_max_height: int = field(default_factory=lambda: int(os.getenv("DOWNLOAD_MAX_HEIGHT", "1080")))
    pot_provider_url: str | None = field(default_factory=lambda: os.getenv("POT_PROVIDER_URL") or None)
    cookies_file: str | None = field(default_factory=lambda: os.getenv("COOKIES_FILE") or None)
    cookie_urls: list[str] = field(
        default_factory=lambda: [u.strip() for u in os.getenv("COOKIE_URLS", "").split(",") if u.strip()]
    )
    cookie_revalidate_minutes: int = field(
        default_factory=lambda: int(os.getenv("COOKIE_REVALIDATE_MINUTES", "360"))
    )


config = Config()
