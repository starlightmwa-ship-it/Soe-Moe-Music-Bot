# plugins/queue.py
from pyrogram.types import Message
from plugins import queues

async def queue_cmd(client, message: Message):
    chat_id = message.chat.id
    
    if chat_id not in queues or not queues[chat_id]:
        await message.reply("📋 Queue is empty!")
        return
    
    text = "**📋 MUSIC QUEUE**\n\n"
    for i, track in enumerate(queues[chat_id][:15], 1):
        text += f"`{i}. {track['title'][:45]}`\n"
    
    if len(queues[chat_id]) > 15:
        text += f"\n... and {len(queues[chat_id]) - 15} more"
    
    await message.reply(text)
