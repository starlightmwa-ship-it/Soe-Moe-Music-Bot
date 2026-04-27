# plugins/
from pyrogram.types import Message
from config import AUTO_DELETE_SECONDS
import asyncio

async def skip(client, message: Message, assistant, queues, bot):
    chat_id = message.chat.id
    
    if queues.get(chat_id) and queues[chat_id]:
        next_track = queues[chat_id].pop(0)
        await assistant.change_stream(chat_id, next_track['url'])
        msg = await message.reply(f"⏭️ Skipped\n▶️ Now: **{next_track['title'][:50]}**")
    else:
        await assistant.leave_group_call(chat_id)
        msg = await message.reply("⏭️ Skipped\n📭 Queue finished!")
    
    await asyncio.sleep(AUTO_DELETE_SECONDS)
    await msg.delete()
    await message.delete()
