# plugins/skip.py
from pyrogram.types import Message
from plugins import queues
from .play import get_audio_url

async def skip(client, message: Message, call):
    chat_id = message.chat.id
    
    if chat_id in queues and queues[chat_id]:
        next_track = queues[chat_id].pop(0)
        audio_url = await get_audio_url(next_track['url'])
        await call.change_stream(chat_id, audio_url)
        await message.reply(f"⏭️ Skipped\n▶️ Now: **{next_track['title'][:50]}**")
    else:
        await call.leave_group_call(chat_id)
        from plugins import active_calls
        active_calls[chat_id] = False
        await message.reply("⏭️ Skipped\n📭 Queue finished!")
