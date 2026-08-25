from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot.config import config
from bot.locales.texts import t
from bot.services.storage import Storage

router = Router(name="admin")
logger = logging.getLogger(__name__)


def _is_admin(user_id: int) -> bool:
    return user_id in config.admin_ids


@router.message(Command("stats"))
async def cmd_stats(message: Message, storage: Storage) -> None:
    user = await storage.get_user(message.from_user.id)
    lang = user.lang if user else "ru"

    if not _is_admin(message.from_user.id):
        await message.answer(t(lang, "admin_only"))
        return

    stats = await storage.stats()
    await message.answer(t(lang, "stats", **stats))


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, bot: Bot, storage: Storage) -> None:
    user = await storage.get_user(message.from_user.id)
    lang = user.lang if user else "ru"

    if not _is_admin(message.from_user.id):
        await message.answer(t(lang, "admin_only"))
        return

    if message.reply_to_message is None:
        await message.answer(t(lang, "broadcast_usage"))
        return

    user_ids = await storage.all_user_ids()
    await message.answer(t(lang, "broadcast_started", total=len(user_ids)))

    sent = 0
    failed = 0
    for user_id in user_ids:
        try:
            await message.reply_to_message.copy_to(user_id)
            sent += 1
        except Exception:
            failed += 1
            logger.warning("broadcast failed for %s", user_id, exc_info=True)
        await asyncio.sleep(config.broadcast_delay_sec)

    await message.answer(t(lang, "broadcast_done", sent=sent, failed=failed))


@router.message(Command("setchannel"))
async def cmd_setchannel(message: Message, command: CommandObject, storage: Storage) -> None:
    user = await storage.get_user(message.from_user.id)
    lang = user.lang if user else "ru"

    if not _is_admin(message.from_user.id):
        await message.answer(t(lang, "admin_only"))
        return

    args = (command.args or "").split()
    if len(args) != 2:
        await message.answer(t(lang, "setchannel_usage"))
        return

    target_lang, channel = args[0].lower(), args[1]
    if target_lang not in ("ru", "en"):
        await message.answer(t(lang, "setchannel_bad_lang"))
        return

    if not channel.startswith("@"):
        channel = f"@{channel}"

    await storage.set_required_channel(target_lang, channel)
    await message.answer(t(lang, "setchannel_done", lang=target_lang, channel=channel))


@router.message(Command("unsetchannel"))
async def cmd_unsetchannel(message: Message, command: CommandObject, storage: Storage) -> None:
    user = await storage.get_user(message.from_user.id)
    lang = user.lang if user else "ru"

    if not _is_admin(message.from_user.id):
        await message.answer(t(lang, "admin_only"))
        return

    args = (command.args or "").split()
    if len(args) != 1 or args[0].lower() not in ("ru", "en"):
        await message.answer(t(lang, "unsetchannel_usage"))
        return

    target_lang = args[0].lower()
    await storage.set_required_channel(target_lang, None)
    await message.answer(t(lang, "unsetchannel_done", lang=target_lang))


@router.message(Command("channels"))
async def cmd_channels(message: Message, storage: Storage) -> None:
    user = await storage.get_user(message.from_user.id)
    lang = user.lang if user else "ru"

    if not _is_admin(message.from_user.id):
        await message.answer(t(lang, "admin_only"))
        return

    channels = await storage.get_required_channels()
    none_label = t(lang, "channels_none")
    await message.answer(
        t(
            lang,
            "channels_status",
            ru=channels.get("ru", none_label),
            en=channels.get("en", none_label),
        )
    )
