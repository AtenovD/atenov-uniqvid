from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

from aiogram import Bot, F, Router
from aiogram.types import FSInputFile, Message

from bot.config import config
from bot.locales.texts import t
from bot.services.explain import explain
from bot.services.storage import Storage
from bot.services.uniquizer import FFmpegError, uniquize

router = Router(name="video")
logger = logging.getLogger(__name__)


async def uniquize_and_reply(
    target: Message, bot: Bot, storage: Storage, lang: str, input_path: Path, work_dir: Path, user_id: int
) -> None:
    """Runs the uniquize pipeline on `input_path` and replies to `target` with the result.

    `user_id` is taken explicitly rather than from `target.from_user` because `target` may be a
    bot-authored message (e.g. the download-result message) whose `from_user` is the bot itself.
    """
    status_msg = await target.answer(t(lang, "processing"))
    try:
        result = await uniquize(input_path, work_dir)
        explanation = explain(result.applied_ops, lang)

        await target.answer_video(
            FSInputFile(result.output_path),
            caption=t(lang, "done_caption", explanation=explanation),
        )
        await storage.log_processed_video(user_id, len(result.applied_ops))
        result.output_path.unlink(missing_ok=True)
    except FFmpegError:
        logger.exception("ffmpeg failed for user %s", user_id)
        await target.answer(t(lang, "error"))
    finally:
        await status_msg.delete()
        input_path.unlink(missing_ok=True)


@router.message(F.video | F.video_note | (F.document & F.document.mime_type.startswith("video/")))
async def on_video(message: Message, bot: Bot, storage: Storage) -> None:
    user = await storage.get_user(message.from_user.id)
    lang = user.lang if user else "ru"

    file_obj = message.video or message.video_note or message.document
    file_size = getattr(file_obj, "file_size", None) or 0
    if file_size and file_size > config.max_video_mb * 1024 * 1024:
        await message.answer(t(lang, "too_large", max_mb=config.max_video_mb))
        return

    work_dir = Path(config.work_dir) / str(message.from_user.id)
    work_dir.mkdir(parents=True, exist_ok=True)
    input_path = work_dir / f"in_{uuid4().hex}.mp4"

    tg_file = await bot.get_file(file_obj.file_id)
    await bot.download_file(tg_file.file_path, destination=input_path)

    await uniquize_and_reply(message, bot, storage, lang, input_path, work_dir, message.from_user.id)


@router.message(F.document)
async def on_non_video_document(message: Message, storage: Storage) -> None:
    user = await storage.get_user(message.from_user.id)
    lang = user.lang if user else "ru"
    await message.answer(t(lang, "not_a_video"))
