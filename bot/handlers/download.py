from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

import aiohttp
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from bot.config import config
from bot.handlers.video import uniquize_and_reply
from bot.keyboards import uniquify_now_keyboard
from bot.locales.texts import t
from bot.services.cookies import CookieManager
from bot.services.downloader import DownloadError, download_video, is_supported_link
from bot.services.storage import Storage

router = Router(name="download")
logger = logging.getLogger(__name__)


async def _lang(storage: Storage, user_id: int) -> str:
    user = await storage.get_user(user_id)
    return user.lang if user else "ru"


@router.message(F.text.func(lambda text: is_supported_link(text)))
async def on_link(
    message: Message,
    bot: Bot,
    storage: Storage,
    state: FSMContext,
    http_session: aiohttp.ClientSession,
    cookie_manager: CookieManager,
) -> None:
    lang = await _lang(storage, message.from_user.id)
    work_dir = Path(config.work_dir) / str(message.from_user.id)

    status_msg = await message.answer(t(lang, "download_progress"))
    try:
        cookies_path = await cookie_manager.get_path(http_session)
        output_path = await download_video(message.text.strip(), work_dir, cookies_path)
    except DownloadError:
        logger.exception("download failed for user %s", message.from_user.id)
        await status_msg.delete()
        await message.answer(t(lang, "download_error"))
        return

    await status_msg.delete()
    await state.update_data(downloaded_path=str(output_path))
    await message.answer_video(
        FSInputFile(output_path),
        caption=t(lang, "download_done_caption"),
        reply_markup=uniquify_now_keyboard(lang),
    )


@router.callback_query(F.data == "postdl:uniquify")
async def on_uniquify_downloaded(callback: CallbackQuery, bot: Bot, storage: Storage, state: FSMContext) -> None:
    lang = await _lang(storage, callback.from_user.id)
    data = await state.get_data()
    path_str = data.get("downloaded_path")

    if not path_str or not Path(path_str).exists():
        await callback.answer()
        await callback.message.answer(t(lang, "download_expired"))
        return

    await callback.answer()
    input_path = Path(path_str)
    work_dir = input_path.parent

    # Re-home under a fresh name so uniquize_and_reply's cleanup can't clash with another concurrent job.
    fresh_path = work_dir / f"in_{uuid4().hex}.mp4"
    input_path.rename(fresh_path)
    await state.update_data(downloaded_path=None)

    await uniquize_and_reply(callback.message, bot, storage, lang, fresh_path, work_dir, callback.from_user.id)
