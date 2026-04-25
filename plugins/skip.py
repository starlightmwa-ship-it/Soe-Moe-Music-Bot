# plugins/skip.py
from pyrogram.types import Message

async def skip(client, message: Message, user, queues):
    chat_id = message.chat.id
    
    if queues.get(chat_id):
        next_track = queues[chat_id].pop(0)
        from pytgcalls import PyTgCalls
        call = PyTgCalls(user)
        await call.change_stream(chat_id, next_track['url'])
        await message.reply(f"⏭️ Skipped\n▶️ Now: **{next_track['title'][:50]}**")
    else:
        await message.reply("❌ Queue is empty!")
