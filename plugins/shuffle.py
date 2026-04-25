# plugins/shuffle.py
import random
from pyrogram.types import Message

async def shuffle(client, message: Message, queues):
    chat_id = message.chat.id
    queue_list = queues.get(chat_id, [])
    
    if len(queue_list) < 2:
        await message.reply("🎲 Need at least 2 songs to shuffle!")
        return
    
    random.shuffle(queue_list)
    await message.reply("🎲 Queue shuffled!")
