# plugins/pause.py
from pyrogram.types import Message
from config import AUTO_DELETE_SECONDS
import asyncio

async def pause(client, message: Message, assistant, queues):
    chat_id = message.chat.id
    if assistant.is_connected(chat_id):
        await assistant.pause_stream(chat_id)
        msg = await message.reply("⏸ Paused")
        await asyncio.sleep(AUTO_DELETE_SECONDS)
        await msg.delete()
        await message.delete()
    else:
        msg = await message.reply("❌ Nothing playing!")
        await asyncio.sleep(AUTO_DELETE_SECONDS)
        await msg.delete()
        await message.delete()
