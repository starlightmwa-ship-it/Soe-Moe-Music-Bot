# plugins/speed.py
from pyrogram.types import Message

async def speed(client, message: Message, user, queues):
    args = message.text.split()
    if len(args) != 2:
        await message.reply("Usage: `/speed 0.5` to `2.0`")
        return
    
    try:
        speed = float(args[1])
        if speed < 0.5 or speed > 2.0:
            raise ValueError
    except:
        await message.reply("❌ Invalid speed! Use 0.5 to 2.0")
        return
    
    chat_id = message.chat.id
    from pytgcalls import PyTgCalls
    call = PyTgCalls(user)
    await call.change_stream(chat_id, speed=speed)
    await message.reply(f"⚡ Speed changed to `{speed}x`")
