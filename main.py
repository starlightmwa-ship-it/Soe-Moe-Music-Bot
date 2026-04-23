import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import assistant as asst
from config import API_ID, API_HASH, BOT_TOKEN

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ================= STATE =================
queues = {}
now_msg = {}
start_time = {}
durations = {}

# ================= PLAY =================
@bot.on_message(filters.command("play"))
async def play(_, msg):
    chat_id = msg.chat.id
    query = " ".join(msg.command[1:])

    if not query:
        return await msg.reply("❗ Song name ထည့်ပါ")

    url, title, thumb, dur = asst.yt(query)

    queues.setdefault(chat_id, [])
    queues[chat_id].append((url, title, thumb, dur))

    # ▶ first song
    if len(queues[chat_id]) == 1:
        await asst.join(chat_id, url)

        start_time[chat_id] = time.time()
        durations[chat_id] = dur

        m = await msg.reply_photo(
            thumb,
            caption=f"🎵 Now Playing\n📀 {title}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏭ Skip", callback_data="skip"),
                 InlineKeyboardButton("⏹ Stop", callback_data="stop")]
            ])
        )

        now_msg[chat_id] = m

    else:
        await msg.reply(f"➕ Added to queue: {title}")

# ================= NEXT =================
async def next_song(chat_id):
    queues[chat_id].pop(0)

    if not queues[chat_id]:
        await asst.leave(chat_id)
        return

    url, title, thumb, dur = queues[chat_id][0]

    await asst.change(chat_id, url)

    start_time[chat_id] = time.time()
    durations[chat_id] = dur

# ================= BUTTON =================
@bot.on_callback_query()
async def cb(_, q):
    chat_id = q.message.chat.id

    if q.data == "skip":
        await next_song(chat_id)

    elif q.data == "stop":
        queues[chat_id] = []
        await asst.leave(chat_id)

    await q.answer()

# ================= AUTO DELETE =================
async def auto_delete(msg, sec=10):
    await asyncio.sleep(sec)
    try:
        await msg.delete()
    except:
        pass

# ================= START =================
@bot.on_message(filters.command("start"))
async def start(_, msg):
    m = await msg.reply(
        "🎵 Advanced Music Bot Ready!\n\n"
        "/play song\n"
        "/stop"
    )
    asyncio.create_task(auto_delete(m, 15))

# ================= STOP =================
@bot.on_message(filters.command("stop"))
async def stop(_, msg):
    chat_id = msg.chat.id

    queues[chat_id] = []
    await asst.leave(chat_id)

    m = await msg.reply("⏹ Stopped")
    asyncio.create_task(auto_delete(m, 10))

# ================= RUN =================
async def main():
    await bot.start()
    await asst.start()
    print("NEXT LEVEL BOT RUNNING")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
