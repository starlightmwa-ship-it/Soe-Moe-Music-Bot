# plugins/speed.py
from pyrogram.types import Message
from config import AUTO_DELETE_SECONDS
import asyncio

async def speed(client, message: Message, assistant, queues):
    args = message.text.split()
    if len(args) != 2:
        msg = await message.reply("Usage: `/speed 0.5` to `2.0`")
        await asyncio.sleep(AUTO_DELETE_SECONDS)
        await msg.delete()
        await message.delete()
        return
    
    try:
        speed = float(args[1])
        if speed < 0.5 or speed > 2.0:
            raise ValueError
    except:
        msg = await message.reply("❌ Invalid speed! Use 0.5 to 2.0")
        await asyncio.sleep(AUTO_DELETE_SECONDS)
        await msg.delete()
        await message.delete()
        return
    
    chat_id = message.chat.id
    await assistant.change_stream(chat_id, speed=speed)
    msg = await message.reply(f"⚡ Speed changed to `{speed}x`")
    await asyncio.sleep(AUTO_DELETE_SECONDS)
    await msg.delete()
    await message.delete()
