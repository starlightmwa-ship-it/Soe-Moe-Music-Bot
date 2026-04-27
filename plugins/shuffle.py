# plugins/
import random
from pyrogram.types import Message
from config import AUTO_DELETE_SECONDS
import asyncio

async def shuffle(client, message: Message, queues):
    chat_id = message.chat.id
    
    if chat_id not in queues or len(queues[chat_id]) < 2:
        msg = await message.reply("🎲 Need at least 2 songs to shuffle!")
        await asyncio.sleep(AUTO_DELETE_SECONDS)
        await msg.delete()
        await message.delete()
        return
    
    random.shuffle(queues[chat_id])
    msg = await message.reply("🎲 Queue shuffled!")
    await asyncio.sleep(AUTO_DELETE_SECONDS)
    await msg.delete()
    await message.delete()
