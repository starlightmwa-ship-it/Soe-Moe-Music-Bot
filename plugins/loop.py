# plugins/loop.py
from pyrogram.types import Message
from plugins import queues

loop_modes = {}

async def loop(client, message: Message):
    chat_id = message.chat.id
    current = loop_modes.get(chat_id, 0)
    current = (current + 1) % 3
    
    loop_modes[chat_id] = current
    mode_text = ["Off", "Single", "Queue"][current]
    
    await message.reply(f"🔄 Loop mode: **{mode_text}**")
