# plugins/queue.py
from pyrogram.types import Message

async def queue_cmd(client, message: Message, queues):
    chat_id = message.chat.id
    queue_list = queues.get(chat_id, [])
    
    if not queue_list:
        await message.reply("📋 Queue is empty!")
        return
    
    text = "**📋 MUSIC QUEUE**\n\n"
    for i, track in enumerate(queue_list[:10], 1):
        text += f"`{i}. {track['title'][:45]}`\n"
    
    if len(queue_list) > 10:
        text += f"\n... and {len(queue_list) - 10} more"
    
    await message.reply(text)
