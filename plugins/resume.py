# plugins/resume.py
from pyrogram.types import Message

async def resume(client, message: Message, user, queues):
    chat_id = message.chat.id
    from pytgcalls import PyTgCalls
    call = PyTgCalls(user)
    await call.resume_stream(chat_id)
    await message.reply("▶️ Resumed")
