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
        "broadcast_started": "📣 Рассылка начата ({total} получателей)...",
        "broadcast_done": "📣 Рассылка завершена: доставлено {sent}, ошибок {failed}.",
        "subscribe_required": (
            "🔒 Чтобы пользоваться ботом, подпишись на канал {channel}, затем нажми «Я подписался»."
        ),
        "subscribe_button": "📢 Открыть канал",
        "subscribe_check_button": "✅ Я подписался",
        "subscribe_still_not": "❌ Пока не вижу подписку. Подпишись и попробуй снова.",
        "subscribe_confirmed": "✅ Подписка подтверждена, теперь бот доступен!",
        "channels_none": "не задан",
        "admin_panel_title": "🛠 Админ-панель",
        "admin_stats_title": "📊 Статистика",
        "admin_broadcast_prompt": "Пришли сообщение (текст, фото, видео — что угодно), которое нужно разослать всем пользователям.",
        "admin_broadcast_cancelled": "Рассылка отменена.",
        "admin_channels_title": "📢 Обязательные каналы подписки",
        "admin_channel_detail": "{flag} Язык: {lang}\nТекущий канал: {channel}",
        "admin_channel_set_prompt": "Пришли username канала (например, @my_channel). Бот должен быть админом в этом канале.",
        "admin_channel_set_done": "✅ Канал для {lang} установлен: {channel}",
        "admin_channel_unset_done": "✅ Обязательная подписка для {lang} отключена.",
        "admin_action_cancelled": "Отменено.",
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
        "broadcast_started": "📣 Broadcast started ({total} recipients)...",
        "broadcast_done": "📣 Broadcast finished: delivered {sent}, failed {failed}.",
        "subscribe_required": (
            "🔒 To use this bot, subscribe to {channel}, then tap \"I've subscribed\"."
        ),
        "subscribe_button": "📢 Open channel",
        "subscribe_check_button": "✅ I've subscribed",
        "subscribe_still_not": "❌ Still not seeing your subscription. Subscribe and try again.",
        "subscribe_confirmed": "✅ Subscription confirmed, the bot is now available!",
        "channels_none": "not set",
        "admin_panel_title": "🛠 Admin panel",
        "admin_stats_title": "📊 Stats",
        "admin_broadcast_prompt": "Send the message (text, photo, video — anything) you want to broadcast to all users.",
        "admin_broadcast_cancelled": "Broadcast cancelled.",
        "admin_channels_title": "📢 Mandatory subscription channels",
        "admin_channel_detail": "{flag} Language: {lang}\nCurrent channel: {channel}",
        "admin_channel_set_prompt": "Send the channel username (e.g. @my_channel). The bot must be an admin in that channel.",
        "admin_channel_set_done": "✅ Channel for {lang} set to: {channel}",
        "admin_channel_unset_done": "✅ Mandatory subscription for {lang} disabled.",
        "admin_action_cancelled": "Cancelled.",
    },
}


def t(lang: str, key: str, **kwargs: object) -> str:
    lang = lang if lang in TEXTS else "ru"
    template = TEXTS[lang].get(key, key)
    return template.format(**kwargs) if kwargs else template
