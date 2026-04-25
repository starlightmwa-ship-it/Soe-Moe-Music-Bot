# plugins/stop.py
from pyrogram.types import Message

async def stop(client, message: Message, user, queues):
    chat_id = message.chat.id
    queues[chat_id] = []
    from pytgcalls import PyTgCalls
    call = PyTgCalls(user)
    await call.leave_group_call(chat_id)
    await message.reply("⛔ Stopped playback")
