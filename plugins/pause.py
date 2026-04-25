# plugins/pause.py
from pyrogram.types import Message

async def pause(client, message: Message, user, queues):
    chat_id = message.chat.id
    from pytgcalls import PyTgCalls
    call = PyTgCalls(user)
    await call.pause_stream(chat_id)
    await message.reply("⏸ Paused")
