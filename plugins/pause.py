# plugins/pause.py
from pyrogram.types import Message

async def pause(client, message: Message, call):
    chat_id = message.chat.id
    try:
        await call.pause_stream(chat_id)
        await message.reply("⏸ Paused")
    except:
        await message.reply("❌ Nothing playing!")
