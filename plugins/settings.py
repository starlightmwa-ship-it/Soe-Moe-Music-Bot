# plugins/settings.py
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import AUTO_DELETE_SECONDS
import asyncio
import json
import aiofiles

async def setting(client, message: Message, group_settings):
    chat_id = message.chat.id
    
    if chat_id not in group_settings:
        group_settings[chat_id] = {'authorized': [], 'admin_only': False, 'language': 'en'}
    
    admin_only = group_settings[chat_id].get('admin_only', False)
    lang = group_settings[chat_id].get('language', 'en')
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🌐 Language: {'🇲🇲 Myanmar' if lang == 'my' else '🇬🇧 English'}", callback_data=f"lang_{chat_id}")],
        [InlineKeyboardButton(f"👑 Admin Only: {'✅ ON' if admin_only else '❌ OFF'}", callback_data=f"admin_{chat_id}")],
        [InlineKeyboardButton("❌ Close", callback_data=f"close_{chat_id}")]
    ])
    
    msg = await message.reply("⚙️ **Settings Panel**", reply_markup=keyboard)
    await asyncio.sleep(AUTO_DELETE_SECONDS * 2)
    await msg.delete()
    await message.delete()

# Callback handlers should be registered in main.py
