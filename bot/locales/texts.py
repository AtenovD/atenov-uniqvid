from __future__ import annotations

TEXTS: dict[str, dict[str, str]] = {
    "ru": {
        "choose_lang": "Привет! Выбери язык:",
        "lang_set": "Язык установлен: Русский 🇷🇺",
        "welcome": (
            "Пришли мне видео — я сделаю его уникальным: изменю картинку, звук и метаданные так, "
            "чтобы платформы не считали его повтором оригинала. После обработки я расскажу, что именно "
            "было изменено и зачем."
        ),
        "processing": "⚙️ Обрабатываю видео, это займёт немного времени...",
        "done_caption": "✅ Готово! Вот что было сделано:\n\n{explanation}",
        "error": "❌ Не получилось обработать видео. Попробуй ещё раз или пришли другой файл.",
        "too_large": "❌ Файл слишком большой (максимум {max_mb} МБ).",
        "not_a_video": "Пришли, пожалуйста, видео файлом или кружком.",
        "admin_only": "⛔ Команда доступна только администраторам.",
        "stats": (
            "📊 Статистика\n\n"
            "Пользователей всего: {users_total}\n"
            "Новых за 24ч: {new_users_24h}\n"
            "Видео обработано всего: {videos_total}\n"
            "Видео за 24ч: {videos_24h}"
        ),
        "broadcast_usage": "Использование: ответь этой командой на сообщение, которое нужно разослать всем пользователям.",
        "broadcast_started": "📣 Рассылка начата ({total} получателей)...",
        "broadcast_done": "📣 Рассылка завершена: доставлено {sent}, ошибок {failed}.",
        "subscribe_required": (
            "🔒 Чтобы пользоваться ботом, подпишись на канал {channel}, затем нажми «Я подписался»."
        ),
        "subscribe_button": "📢 Открыть канал",
        "subscribe_check_button": "✅ Я подписался",
        "subscribe_still_not": "❌ Пока не вижу подписку. Подпишись и попробуй снова.",
        "subscribe_confirmed": "✅ Подписка подтверждена, теперь бот доступен!",
        "setchannel_usage": "Использование: /setchannel <ru|en> <@канал>",
        "setchannel_bad_lang": "Язык должен быть ru или en.",
        "setchannel_done": "✅ Обязательный канал для {lang}: {channel}",
        "unsetchannel_usage": "Использование: /unsetchannel <ru|en>",
        "unsetchannel_done": "✅ Обязательная подписка для {lang} отключена.",
        "channels_status": "📋 Обязательные каналы:\nru: {ru}\nen: {en}",
        "channels_none": "не задан",
    },
    "en": {
        "choose_lang": "Hi! Choose your language:",
        "lang_set": "Language set: English 🇬🇧",
        "welcome": (
            "Send me a video — I'll uniquify it: alter the picture, sound and metadata so platforms "
            "won't flag it as a repost of the original. After processing I'll explain exactly what was "
            "changed and why."
        ),
        "processing": "⚙️ Processing your video, this will take a moment...",
        "done_caption": "✅ Done! Here's what was changed:\n\n{explanation}",
        "error": "❌ Couldn't process this video. Try again or send another file.",
        "too_large": "❌ File is too large (max {max_mb} MB).",
        "not_a_video": "Please send a video file or video note.",
        "admin_only": "⛔ This command is for admins only.",
        "stats": (
            "📊 Stats\n\n"
            "Total users: {users_total}\n"
            "New in 24h: {new_users_24h}\n"
            "Videos processed total: {videos_total}\n"
            "Videos in 24h: {videos_24h}"
        ),
        "broadcast_usage": "Usage: reply to the message you want to broadcast with this command.",
        "broadcast_started": "📣 Broadcast started ({total} recipients)...",
        "broadcast_done": "📣 Broadcast finished: delivered {sent}, failed {failed}.",
        "subscribe_required": (
            "🔒 To use this bot, subscribe to {channel}, then tap \"I've subscribed\"."
        ),
        "subscribe_button": "📢 Open channel",
        "subscribe_check_button": "✅ I've subscribed",
        "subscribe_still_not": "❌ Still not seeing your subscription. Subscribe and try again.",
        "subscribe_confirmed": "✅ Subscription confirmed, the bot is now available!",
        "setchannel_usage": "Usage: /setchannel <ru|en> <@channel>",
        "setchannel_bad_lang": "Language must be ru or en.",
        "setchannel_done": "✅ Required channel for {lang}: {channel}",
        "unsetchannel_usage": "Usage: /unsetchannel <ru|en>",
        "unsetchannel_done": "✅ Mandatory subscription for {lang} disabled.",
        "channels_status": "📋 Required channels:\nru: {ru}\nen: {en}",
        "channels_none": "not set",
    },
}


def t(lang: str, key: str, **kwargs: object) -> str:
    lang = lang if lang in TEXTS else "ru"
    template = TEXTS[lang].get(key, key)
    return template.format(**kwargs) if kwargs else template
