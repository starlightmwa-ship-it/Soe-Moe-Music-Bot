from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.command("settings"))
async def settings(_, message):
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇲🇲 Myanmar", callback_data="lang_mm"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
        ],
        [
            InlineKeyboardButton("👮 Admin Only", callback_data="admin_toggle")
        ]
    ])
    await message.reply("⚙ Settings:", reply_markup=kb)
