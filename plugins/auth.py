# plugins/
from pyrogram.types import Message
from config import AUTO_DELETE_SECONDS
import asyncio

async def auth(client, message: Message, group_settings):
    chat_id = message.chat.id
    reply = message.reply_to_message
    
    if not reply:
        msg = await message.reply("⚠️ Reply to a user to authorize!")
        await asyncio.sleep(AUTO_DELETE_SECONDS)
        await msg.delete()
        await message.delete()
        return
    
    user_id = reply.from_user.id
    
    if chat_id not in group_settings:
        group_settings[chat_id] = {'authorized': [], 'admin_only': False}
    
    if user_id not in group_settings[chat_id]['authorized']:
        group_settings[chat_id]['authorized'].append(user_id)
    
    msg = await message.reply(f"✅ Authorized user!")
    await asyncio.sleep(AUTO_DELETE_SECONDS)
    await msg.delete()
    await message.delete()

async def unauth(client, message: Message, group_settings):
    chat_id = message.chat.id
    reply = message.reply_to_message
    
    if not reply:
        msg = await message.reply("⚠️ Reply to a user to unauthorize!")
        await asyncio.sleep(AUTO_DELETE_SECONDS)
        await msg.delete()
        await message.delete()
        return
    
    user_id = reply.from_user.id
    
    if chat_id in group_settings and user_id in group_settings[chat_id].get('authorized', []):
        group_settings[chat_id]['authorized'].remove(user_id)
    
    msg = await message.reply(f"❌ Unauthorized user!")
    await asyncio.sleep(AUTO_DELETE_SECONDS)
    await msg.delete()
    await message.delete()
