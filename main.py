# main.py
import asyncio
import sys
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, ASSISTANT_SESSION

# ------- Event Loop Fix for Python 3.14+ -------
if sys.version_info[:2] >= (3, 14):
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
# ------------------------------------------------

print("=" * 50)
print("🎵 SOE MOE MUSIC BOT STARTING...")
print("=" * 50)

# Initialize Bot and Assistant
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=ASSISTANT_SESSION)

# Import plugins
from plugins import (
    play, pause, resume, skip, stop, queue_cmd,
    loop, shuffle, speed, auth, unauth, setting
)

# Global queue and settings storage
queues = {}
group_settings = {}

# ==================== COMMAND HANDLERS ====================

@bot.on_message(filters.command(["start", "help"]))
async def start_cmd(client, message):
    text = """
🎵 **Soe Moe Music Bot** 🎵

**Commands:**
`/play` `<song>` - Play music
`/pause` - Pause playback
`/resume` - Resume playback
`/skip` - Skip current track
`/stop` - Stop playback
`/queue` - Show queue
`/loop` - Toggle loop mode
`/shuffle` - Shuffle queue
`/speed` `<0.5-2.0>` - Change speed
`/auth` `<reply>` - Authorize user
`/unauth` `<reply>` - Remove user
`/setting` - Bot settings

**Made with ❤️**
"""
    await message.reply(text)

@bot.on_message(filters.command("play"))
async def play_handler(client, message):
    await play(client, message, bot, assistant, queues, group_settings)

@bot.on_message(filters.command("pause"))
async def pause_handler(client, message):
    await pause(client, message, assistant, queues)

@bot.on_message(filters.command("resume"))
async def resume_handler(client, message):
    await resume(client, message, assistant, queues)

@bot.on_message(filters.command("skip"))
async def skip_handler(client, message):
    await skip(client, message, assistant, queues, bot)

@bot.on_message(filters.command("stop"))
async def stop_handler(client, message):
    await stop(client, message, assistant, queues, bot)

@bot.on_message(filters.command("queue"))
async def queue_handler(client, message):
    await queue_cmd(client, message, queues)

@bot.on_message(filters.command("loop"))
async def loop_handler(client, message):
    await loop(client, message, queues)

@bot.on_message(filters.command("shuffle"))
async def shuffle_handler(client, message):
    await shuffle(client, message, queues)

@bot.on_message(filters.command("speed"))
async def speed_handler(client, message):
    await speed(client, message, assistant, queues)

@bot.on_message(filters.command("auth"))
async def auth_handler(client, message):
    await auth(client, message, group_settings)

@bot.on_message(filters.command("unauth"))
async def unauth_handler(client, message):
    await unauth(client, message, group_settings)

@bot.on_message(filters.command("setting"))
async def setting_handler(client, message):
    await setting(client, message, group_settings)

# Keep-alive ping every 10 minutes
async def keep_alive():
    while True:
        await asyncio.sleep(600)
        print("🏓 Keep-alive ping - Bot is running")

async def main():
    await bot.start()
    await assistant.start()
    
    print("✅ Bot started successfully!")
    print("✅ Assistant connected!")
    print("✅ Voice Chat ready!")
    print("=" * 50)
    
    asyncio.create_task(keep_alive())
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
