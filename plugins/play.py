from pyrogram import Client, filters
from core.youtube import search
from core.queue import add, get_queue
from core.player import join_and_play
from plugins.player_ui import buttons
import asyncio

async def auto_delete(msg):
    await asyncio.sleep(10)
    try:
        await msg.delete()
    except:
        pass

@Client.on_message(filters.command("play"))
async def play(client, message):
    if len(message.command) < 2:
        return

    query = " ".join(message.command[1:])
    data = search(query)

    song = {"title": data["title"], "url": data["url"], "thumb": data["thumb"]}

    queue = get_queue(message.chat.id)

    if not queue:
        add(message.chat.id, song)
        msg = await message.reply_photo(
            song["thumb"],
            caption=f"🎶 {song['title']}",
            reply_markup=buttons()
        )
        await join_and_play(message.chat.id, song["url"])
    else:
        msg = await message.reply(f"➕ {song['title']}")
        add(message.chat.id, song)

    asyncio.create_task(auto_delete(message))
    asyncio.create_task(auto_delete(msg))
