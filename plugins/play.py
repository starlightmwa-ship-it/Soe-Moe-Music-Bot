from pyrogram import Client, filters
from core.youtube import search
from core.queue import add, get_queue
from core.player import join_and_play

@Client.on_message(filters.command("play"))
async def play(client, message):
    chat_id = message.chat.id

    if len(message.command) < 2:
        return await message.reply("❌ Give song name")

    query = " ".join(message.command[1:])
    data = search(query)

    song = {
        "title": data["title"],
        "url": data["url"],
        "thumb": data["thumb"]
    }

    queue = get_queue(chat_id)

    if not queue:
        add(chat_id, song)
        await join_and_play(chat_id, song["url"])
        await message.reply_photo(
            song["thumb"],
            caption=f"▶️ Now Playing:\n{song['title']}"
        )
    else:
        add(chat_id, song)
        await message.reply(f"➕ Added: {song['title']}")
