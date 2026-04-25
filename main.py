# main.py
import asyncio
import sys
from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN, ASSISTANT_SESSION

# ------- Event Loop Fix -------
if sys.version_info[:2] >= (3, 10):
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
# ------------------------------

print("=" * 50)
print("🎵 FALLEN MUSIC BOT STARTING...")
print("=" * 50)

# Initialize Clients
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("user", api_id=API_ID, api_hash=API_HASH, session_string=ASSISTANT_SESSION)

# Import plugins
from plugins import queues, play, pause, resume, skip, stop, queue_cmd, loop, shuffle, speed

# Global storage
queues: dict = {}

# Register commands
@bot.on_message(filters.command(["play"], prefixes="/"))
async def play_handler(client, message):
    await play(client, message, bot, user, queues)

@bot.on_message(filters.command(["pause"], prefixes="/"))
async def pause_handler(client, message):
    await pause(client, message, user, queues)

@bot.on_message(filters.command(["resume"], prefixes="/"))
async def resume_handler(client, message):
    await resume(client, message, user, queues)

@bot.on_message(filters.command(["skip"], prefixes="/"))
async def skip_handler(client, message):
    await skip(client, message, user, queues)

@bot.on_message(filters.command(["stop", "end"], prefixes="/"))
async def stop_handler(client, message):
    await stop(client, message, user, queues)

@bot.on_message(filters.command(["queue"], prefixes="/"))
async def queue_handler(client, message):
    await queue_cmd(client, message, queues)

@bot.on_message(filters.command(["loop"], prefixes="/"))
async def loop_handler(client, message):
    await loop(client, message, queues)

@bot.on_message(filters.command(["shuffle"], prefixes="/"))
async def shuffle_handler(client, message):
    await shuffle(client, message, queues)

@bot.on_message(filters.command(["speed"], prefixes="/"))
async def speed_handler(client, message):
    await speed(client, message, user, queues)

@bot.on_message(filters.command(["start", "help"], prefixes="/"))
async def start_handler(client, message):
    await message.reply(
        "🎵 **Fallen Music Bot**\n\n"
        "**Commands:**\n"
        "`/play` `<song>` - Play a song\n"
        "`/pause` - Pause playback\n"
        "`/resume` - Resume playback\n"
        "`/skip` - Skip current track\n"
        "`/stop` - Stop playback\n"
        "`/queue` - Show queue\n"
        "`/loop` - Toggle loop mode\n"
        "`/shuffle` - Shuffle queue\n"
        "`/speed` `<0.5-2.0>` - Change speed"
    )

async def main():
    await bot.start()
    await user.start()
    print("✅ Bot started successfully!")
    print("✅ Assistant connected!")
    print("=" * 50)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
