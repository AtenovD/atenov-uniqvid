# UniqVid Bot

Telegram-бот, который принимает видео и делает его уникальным: меняет картинку, звук и метаданные так, чтобы соцсети не считали ролик повтором оригинала. После обработки бот присылает читаемое объяснение — что именно было изменено и зачем (на русском или английском, в зависимости от выбора пользователя).

## Возможности

- Приём видео файлом или видео-кружком
- Случайный набор трансформаций на каждый запуск: масштаб+обрезка, микроповорот, цветокоррекция, зерно, дрейфующая скан-линия, микрорамка, изменение скорости, сдвиг тона звука, фейды, полная пересборка метаданных
- Пояснение на языке пользователя, что применено и почему
- Выбор языка интерфейса: 🇷🇺 русский / 🇬🇧 английский
- Админ-команды прямо в боте: `/stats` (статистика), `/broadcast` (рассылка всем пользователям, ответом на сообщение)

## Стек

Python 3.12, [aiogram 3](https://docs.aiogram.dev/), ffmpeg (через subprocess), aiosqlite.

## Быстрый старт

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # впиши BOT_TOKEN и ADMIN_IDS
python -m bot.main
```

Требуется установленный `ffmpeg`/`ffprobe` в PATH.

## Деплой на VPS (systemd)

```bash
sudo mkdir -p /opt/uniqvid-bot
sudo cp -r . /opt/uniqvid-bot
cd /opt/uniqvid-bot
python3 -m venv venv && venv/bin/pip install -r requirements.txt
cp .env.example .env  # заполнить
sudo cp deploy/uniqvid-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now uniqvid-bot
```

## Деплой через Docker

```bash
docker build -t uniqvid-bot .
docker run -d --env-file .env --restart unless-stopped uniqvid-bot
```

## Конфигурация (`.env`)

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | токен бота от @BotFather |
| `ADMIN_IDS` | ID администраторов через запятую |
| `MAX_VIDEO_MB` | лимит размера входного видео |
| `WORK_DIR` | папка для временных файлов |

## Лицензия

MIT — см. [LICENSE](LICENSE).
