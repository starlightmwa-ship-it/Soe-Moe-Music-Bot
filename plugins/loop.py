# plugins/
from pyrogram.types import Message
from config import AUTO_DELETE_SECONDS
import asyncio

loop_modes = {}

async def loop(client, message: Message, queues):
    chat_id = message.chat.id
    current = loop_modes.get(chat_id, 0)
    current = (current + 1) % 3
    
    loop_modes[chat_id] = current
    mode_text = ["Off", "Single", "Queue"][current]
    
    msg = await message.reply(f"🔄 Loop mode: **{mode_text}**")
    await asyncio.sleep(AUTO_DELETE_SECONDS)
    await msg.delete()
    await message.delete()
