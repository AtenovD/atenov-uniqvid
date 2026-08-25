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
- Optional mandatory-subscription gate, configurable per language: if set, every message is checked against that language's required channel before the bot responds; if unset, the bot works with no restriction
- Admin commands right inside the bot: `/stats` (usage stats), `/broadcast` (message all users, as a reply), `/setchannel <ru|en> <@channel>` / `/unsetchannel <ru|en>` / `/channels` (manage the mandatory-subscription gate)

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

## Mandatory subscription gate

Admins can require users to subscribe to a Telegram channel before using the bot — a separate channel per interface language, or none at all.

```
/setchannel ru @your_ru_channel     # require subscription for Russian-speaking users
/setchannel en @your_en_channel     # require subscription for English-speaking users
/unsetchannel ru                    # disable the requirement for a language
/channels                           # show current configuration
```

The bot must be an **admin in the target channel** to be able to check membership. When a language has no channel configured, users in that language use the bot with no restriction. When it does, the check runs on every incoming message; a subscribed user sees nothing extra — an unsubscribed one gets a prompt with a link to the channel and an "I've subscribed" recheck button.

## License

MIT — see [LICENSE](LICENSE).
