from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.settings import get_settings
from core.lang import t

def settings_buttons(lang, admin_only):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇲🇲 Myanmar", callback_data="lang_mm"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
        ],
        [
            InlineKeyboardButton(
                "👮 Admin: ON" if admin_only else "👮 Admin: OFF",
                callback_data="admin_toggle"
            )
        ]
    ])

@Client.on_message(filters.command("settings"))
async def settings_cmd(client, message):
    data = await get_settings(message.chat.id)

    await message.reply(
        t(data["lang"], "settings"),
        reply_markup=settings_buttons(data["lang"], data["admin_only"])
    )
