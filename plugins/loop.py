# plugins/loop.py
from pyrogram.types import Message

loop_modes = {}  # chat_id: 0=off, 1=on

async def loop(client, message: Message, queues):
    chat_id = message.chat.id
    current = loop_modes.get(chat_id, 0)
    loop_modes[chat_id] = 1 - current
    
    mode_text = "ON" if loop_modes[chat_id] else "OFF"
    await message.reply(f"🔄 Loop mode: **{mode_text}**")
