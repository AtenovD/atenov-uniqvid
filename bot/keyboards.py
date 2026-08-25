from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            ]
        ]
    )


def admin_entry_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🛠 Admin panel", callback_data="admin:open")]]
    )


def admin_root_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Stats", callback_data="admin:stats")],
            [InlineKeyboardButton(text="📣 Broadcast", callback_data="admin:broadcast")],
            [InlineKeyboardButton(text="📢 Channels", callback_data="admin:channels")],
        ]
    )


def back_keyboard(target: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅ Back", callback_data=target)]]
    )


def cancel_keyboard(target: str = "admin:open") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="✖ Cancel", callback_data=target)]]
    )


def admin_channels_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇷🇺 RU channel", callback_data="admin:channel:ru"),
                InlineKeyboardButton(text="🇬🇧 EN channel", callback_data="admin:channel:en"),
            ],
            [InlineKeyboardButton(text="⬅ Back", callback_data="admin:open")],
        ]
    )


def admin_channel_detail_keyboard(lang: str, has_channel: bool) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text="✏️ Set channel", callback_data=f"admin:channel:set:{lang}")]]
    if has_channel:
        rows.append(
            [InlineKeyboardButton(text="🗑 Unset channel", callback_data=f"admin:channel:unset:{lang}")]
        )
    rows.append([InlineKeyboardButton(text="⬅ Back", callback_data="admin:channels")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
