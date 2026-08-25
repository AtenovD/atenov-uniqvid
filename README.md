<p align="center">
  <img src="assets/pipeline-banner.svg" alt="UniqVid Bot pipeline overview" width="100%">
</p>

<h1 align="center">UniqVid Bot</h1>

<p align="center">
  A Telegram bot that takes a video and makes it unique — it alters the picture, sound and metadata so platforms stop treating the clip as a repost of the original. After processing, it explains exactly what was changed and why, in the user's own language.
</p>

## Features

- Accepts a video as a file or a video-note
- A random subset of transforms on every run: zoom+crop, micro-rotate, color grading, film grain, drifting scanline, micro border, speed shift, audio pitch shift, fades, full metadata rebuild
- Plain-language explanation of what was applied and why, in the user's language
- Interface language picker: 🇷🇺 Russian / 🇬🇧 English
- Admin commands right inside the bot: `/stats` (usage stats), `/broadcast` (message all users, as a reply)

## Stack

Python 3.12, [aiogram 3](https://docs.aiogram.dev/), ffmpeg (via subprocess), aiosqlite.

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
| `MAX_VIDEO_MB` | max size of an input video |
| `WORK_DIR` | scratch folder for temporary files |

## License

MIT — see [LICENSE](LICENSE).
