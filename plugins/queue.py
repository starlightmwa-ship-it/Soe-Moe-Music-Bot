# plugins/
from pyrogram.types import Message
from config import AUTO_DELETE_SECONDS
import asyncio

async def queue_cmd(client, message: Message, queues):
    chat_id = message.chat.id
    
    if chat_id not in queues or not queues[chat_id]:
        msg = await message.reply("📋 Queue is empty!")
        await asyncio.sleep(AUTO_DELETE_SECONDS)
        await msg.delete()
        await message.delete()
        return
    
    text = "**📋 MUSIC QUEUE**\n\n"
    for i, track in enumerate(queues[chat_id][:15], 1):
        text += f"`{i}. {track['title'][:45]}`\n"
    
    if len(queues[chat_id]) > 15:
        text += f"\n... and {len(queues[chat_id]) - 15} more"
    
    msg = await message.reply(text)
    await asyncio.sleep(AUTO_DELETE_SECONDS)
    await msg.delete()
    await message.delete()
