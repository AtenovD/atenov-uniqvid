from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from bot.config import config
from bot.keyboards import admin_entry_keyboard, language_keyboard
from bot.locales.texts import t
from bot.services.storage import Storage

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, storage: Storage) -> None:
    user = await storage.get_user(message.from_user.id)
    if user is None:
        await storage.upsert_user(message.from_user.id, message.from_user.username)
        await message.answer(t("ru", "choose_lang"), reply_markup=language_keyboard())
        return

    await storage.upsert_user(message.from_user.id, message.from_user.username)
    keyboard = admin_entry_keyboard() if message.from_user.id in config.admin_ids else None
    await message.answer(t(user.lang, "welcome"), reply_markup=keyboard)


@router.callback_query(F.data.startswith("lang:"))
async def on_lang_chosen(callback: CallbackQuery, storage: Storage) -> None:
    lang = callback.data.split(":", 1)[1]
    await storage.upsert_user(callback.from_user.id, callback.from_user.username, lang=lang)
    await callback.message.edit_text(t(lang, "lang_set"))
    keyboard = admin_entry_keyboard() if callback.from_user.id in config.admin_ids else None
    await callback.message.answer(t(lang, "welcome"), reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "check_sub")
async def on_check_sub(callback: CallbackQuery, storage: Storage) -> None:
    # Reached only once SubscriptionMiddleware has confirmed the user is now subscribed.
    user = await storage.get_user(callback.from_user.id)
    lang = user.lang if user else "ru"
    await callback.answer(t(lang, "subscribe_confirmed"), show_alert=True)
    if callback.message:
        await callback.message.delete()
