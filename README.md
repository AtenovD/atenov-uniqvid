<p align="center">
  <img src="assets/pipeline-banner.svg" alt="UniqVid Bot pipeline overview" width="100%">
</p>

<p align="center">
  <img src="assets/chat-preview.svg" alt="UniqVid Bot chat preview" width="100%">
</p>

<h1 align="center">UniqVid Bot</h1>

<p align="center">
  A Telegram bot that takes a video and makes it unique — it alters the picture, sound and metadata so platforms stop treating the clip as a repost of the original. After processing, it explains exactly what was changed and why, in the user's own language.
</p>

## Features

- Accepts a video as a file, a video-note, **or a YouTube/Instagram Reels link** — the bot downloads it as MP4 via `yt-dlp` and offers to uniquify it right away
- A random subset of transforms on every run: zoom+crop, micro-rotate, color grading, film grain, drifting scanline, micro border, speed shift, audio pitch shift, fades, full metadata rebuild
- Plain-language explanation of what was applied and why, in the user's language
- Interface language picker: 🇷🇺 Russian / 🇬🇧 English
- Optional mandatory-subscription gate, configurable per language: if set, every message is checked against that language's required channel before the bot responds; if unset, the bot works with no restriction
- No slash commands beyond `/start` — everything (including the whole admin panel) is driven by inline buttons

## Stack

Python 3.12, [aiogram 3](https://docs.aiogram.dev/), ffmpeg (via subprocess), [yt-dlp](https://github.com/yt-dlp/yt-dlp), aiosqlite.

## Quick start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in BOT_TOKEN and ADMIN_IDS
python -m bot.main
```

Requires `ffmpeg`/`ffprobe` available on `PATH`.

## Deploy on a VPS (systemd)

```bash
sudo mkdir -p /opt/uniqvid-bot
sudo cp -r . /opt/uniqvid-bot
cd /opt/uniqvid-bot
python3 -m venv venv && venv/bin/pip install -r requirements.txt
cp .env.example .env  # fill in
sudo cp deploy/uniqvid-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now uniqvid-bot
```

## Deploy with Docker

```bash
docker build -t uniqvid-bot .
docker run -d --env-file .env --restart unless-stopped uniqvid-bot
```

## Configuration (`.env`)

| Variable | Description |
|---|---|
| `BOT_TOKEN` | bot token from @BotFather |
| `ADMIN_IDS` | comma-separated admin user IDs |
| `MAX_VIDEO_MB` | max size of an input video, also caps link downloads |
| `WORK_DIR` | scratch folder for temporary files |
| `DOWNLOAD_MAX_HEIGHT` | resolution cap for link downloads (default `1080`) |
| `POT_PROVIDER_URL` | optional, e.g. `http://pot-provider:4416` — see below |
| `COOKIES_FILE` | optional path to a Netscape-format `cookies.txt` — alternative to a PO Token provider |

## Downloading from a link

Send a YouTube or Instagram Reels URL instead of a file, and the bot will:

1. Download it as MP4 with `yt-dlp` (capped at `MAX_VIDEO_MB`)
2. Send the MP4 back with a "✨ Uniquify this video" button
3. Run the same randomized pipeline on it if you tap that button

Only download and reprocess content you actually have the right to use — the bot doesn't check licensing for you.

### Getting higher-than-360p YouTube downloads

By default, YouTube downloads are capped at roughly 360p. That's not a bug — as of 2025, YouTube requires a **PO Token** to serve its web client's higher-quality formats, and `yt-dlp` falls back to the low-quality android client when one isn't available. Two ways to unlock full quality (up to `DOWNLOAD_MAX_HEIGHT`):

1. **PO Token provider (recommended)** — run the bundled sidecar, no personal account needed:
   ```bash
   docker compose up -d
   ```
   `docker-compose.yml` starts the bot alongside [`bgutil-ytdlp-pot-provider`](https://github.com/Brainicism/bgutil-ytdlp-pot-provider) and wires `POT_PROVIDER_URL` automatically. That project's server component is GPL-3.0 licensed; it only talks to the bot over HTTP as a separate service, so it doesn't affect this project's own MIT license.
2. **Authenticated cookies** — export a `cookies.txt` from a logged-in YouTube session (e.g. with a browser extension) and set `COOKIES_FILE=/path/to/cookies.txt`. Simpler to set up, but ties downloads to that account and needs the file refreshed if it expires.

Without either, the bot still works — it just downloads at ~360p.

## Admin panel

Any user ID listed in `ADMIN_IDS` sees a "🛠 Admin panel" button under `/start`. It opens an inline-button menu:

- **📊 Stats** — total users, new users in 24h, videos processed
- **📣 Broadcast** — bot asks for a message, then forwards it to every known user
- **📢 Channels** — set or unset the mandatory-subscription channel per interface language (🇷🇺 / 🇬🇧)

The bot must be an **admin in the target channel** to be able to check membership. When a language has no channel configured, users in that language use the bot with no restriction. When it does, the check runs on every incoming message; a subscribed user sees nothing extra — an unsubscribed one gets a prompt with a link to the channel and an "I've subscribed" recheck button.

## License

MIT — see [LICENSE](LICENSE).
