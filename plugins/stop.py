# plugins/stop.py
from pyrogram.types import Message
from plugins import queues, active_calls

async def stop(client, message: Message, call):
    chat_id = message.chat.id
    
    await call.leave_group_call(chat_id)
    if chat_id in queues:
        queues[chat_id].clear()
    active_calls[chat_id] = False
    
    await message.reply("⛔ Stopped playback")
