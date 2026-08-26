from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path
from uuid import uuid4

from bot.config import config

_SUPPORTED_RE = re.compile(r"(youtube\.com|youtu\.be|instagram\.com)", re.IGNORECASE)


class DownloadError(RuntimeError):
    pass


def is_supported_link(text: str) -> bool:
    return bool(_SUPPORTED_RE.search(text))


def _build_args(url: str, out_template: str) -> list[str]:
    height = config.download_max_height
    has_po_source = bool(config.pot_provider_url or config.cookies_file)

    args = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--no-playlist",
        "--no-warnings",
    ]

    if has_po_source:
        # With a PO Token source (provider or authenticated cookies), the web client is unlocked
        # and can serve full quality; android stays as a fallback if web extraction fails.
        args += ["--extractor-args", "youtube:player_client=web,android"]
        if config.pot_provider_url:
            args += ["--extractor-args", f"youtubepot-bgutilhttp:base_url={config.pot_provider_url}"]
        if config.cookies_file:
            args += ["--cookies", config.cookies_file]
    else:
        # No PO Token source configured: the web client triggers YouTube's SABR restrictions, and
        # android/ios without a token are capped at ~360p. This is the safe, zero-setup default.
        args += ["--extractor-args", "youtube:player_client=android,web"]

    args += [
        "-f",
        f"bv*[ext=mp4][height<={height}]+ba[ext=m4a]/b[ext=mp4][height<={height}]/best[height<={height}]/best",
        "--merge-output-format",
        "mp4",
        "--max-filesize",
        f"{config.max_video_mb}M",
        "-o",
        out_template,
        url,
    ]
    return args


async def download_video(url: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"dl_{uuid4().hex}"
    out_template = str(out_dir / f"{stem}.%(ext)s")

    args = _build_args(url, out_template)

    proc = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await proc.communicate()

    matches = sorted(out_dir.glob(f"{stem}.*"))
    if proc.returncode != 0 or not matches:
        for f in matches:
            f.unlink(missing_ok=True)
        raise DownloadError(stderr.decode(errors="ignore")[-1500:])

    output_path = matches[0]

    if output_path.suffix.lower() != ".mp4":
        remuxed = out_dir / f"{stem}.mp4"
        remux = await asyncio.create_subprocess_exec(
            config.ffmpeg_bin,
            "-y",
            "-i",
            str(output_path),
            "-c",
            "copy",
            str(remuxed),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, remux_err = await remux.communicate()
        output_path.unlink(missing_ok=True)
        if remux.returncode != 0 or not remuxed.exists():
            raise DownloadError(remux_err.decode(errors="ignore")[-1500:])
        output_path = remuxed

    if output_path.stat().st_size > config.max_video_mb * 1024 * 1024:
        output_path.unlink(missing_ok=True)
        raise DownloadError("downloaded file exceeds the configured size limit")

    return output_path
