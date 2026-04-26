from pyrogram import Client, filters
from core.queue import pop, get_queue
from core.player import join_and_play

@Client.on_message(filters.command("skip"))
async def skip(_, message):
    chat_id = message.chat.id

    pop(chat_id)
    queue = get_queue(chat_id)

    if not queue:
        return await message.reply("❌ Queue empty")

    song = queue[0]
    await join_and_play(chat_id, song["url"])
    await message.reply(f"⏭ {song['title']}")
