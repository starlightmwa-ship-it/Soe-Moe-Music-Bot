# plugins/shuffle.py
import random
from pyrogram.types import Message
from plugins import queues

async def shuffle(client, message: Message):
    chat_id = message.chat.id
    
    if chat_id not in queues or len(queues[chat_id]) < 2:
        await message.reply("🎲 Need at least 2 songs to shuffle!")
        return
    
    random.shuffle(queues[chat_id])
    await message.reply("🎲 Queue shuffled!")
