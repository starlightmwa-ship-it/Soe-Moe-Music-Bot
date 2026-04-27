# plugins/
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import AUTO_DELETE_SECONDS
import asyncio

async def stop(client, message: Message, assistant, queues, bot):
    chat_id = message.chat.id
    await assistant.leave_group_call(chat_id)
    if chat_id in queues:
        queues[chat_id].clear()
    msg = await message.reply("⛔ Stopped playback")
    await asyncio.sleep(AUTO_DELETE_SECONDS)
    await msg.delete()
    await message.delete()
