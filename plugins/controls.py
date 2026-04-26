from pyrogram import Client
from core.player import stop
from core.queue import pop, get_queue
from core.player import join_and_play

@Client.on_callback_query()
async def cb(client, cb):
    chat_id = cb.message.chat.id

    if cb.data == "skip":
        pop(chat_id)
        q = get_queue(chat_id)
        if q:
            await join_and_play(chat_id, q[0]["url"])

    elif cb.data == "stop":
        await stop(chat_id)

    await cb.answer()
