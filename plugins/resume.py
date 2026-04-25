# plugins/resume.py
from pyrogram.types import Message

async def resume(client, message: Message, call):
    chat_id = message.chat.id
    try:
        await call.resume_stream(chat_id)
        await message.reply("▶️ Resumed")
    except:
        await message.reply("❌ Nothing playing!")
