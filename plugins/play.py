from pyrogram import Client, filters
from pyrogram.types import ChatMemberStatus
from core.youtube import search
from core.queue import add, get_queue
from core.player import join_and_play
from plugins.player_ui import buttons
from database.settings import get_settings
from core.lang import t
import asyncio

# ✅ Admin check
async def is_admin(client, message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]

# 🧹 Auto delete
async def auto_delete(msg):
    await asyncio.sleep(10)
    try:
        await msg.delete()
    except:
        pass

@Client.on_message(filters.command("play") & filters.group)
async def play(client, message):
    chat_id = message.chat.id

    settings = await get_settings(chat_id)
    lang = settings["lang"]

    # 🔐 Admin only check
    if settings["admin_only"]:
        if not await is_admin(client, message):
            return await message.reply(t(lang, "no_admin"))

    # ❌ no query
    if len(message.command) < 2:
        m = await message.reply("❌ Give song name")
        asyncio.create_task(auto_delete(m))
        asyncio.create_task(auto_delete(message))
        return

    query = " ".join(message.command[1:])

    # 🔍 search youtube
    data = search(query)

    song = {
        "title": data["title"],
        "url": data["url"],
        "thumb": data["thumb"]
    }

    queue = get_queue(chat_id)

    # ▶️ play or queue
    if not queue:
        add(chat_id, song)

        msg = await message.reply_photo(
            song["thumb"],
            caption=f"🎶 {song['title']}",
            reply_markup=buttons()
        )

        await join_and_play(chat_id, song["url"])

    else:
        add(chat_id, song)
        msg = await message.reply(f"➕ {song['title']}")

    # 🧹 auto delete
    asyncio.create_task(auto_delete(message))
    asyncio.create_task(auto_delete(msg))
