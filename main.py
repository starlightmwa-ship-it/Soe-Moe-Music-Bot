# main.py
import asyncio
import sys
from pyrogram import Client
from pytgcalls import PyTgCalls
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING, OWNER_ID

# ------- Event Loop Fix for Python 3.10+ -------
import asyncio
if sys.version_info[:2] >= (3, 10):
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
# ------------------------------------------------

print("=" * 50)
print("🎵 FALLEN MUSIC BOT STARTING...")
print("=" * 50)

# Initialize Clients
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# Initialize PyTgCalls with user client
call = PyTgCalls(user)

# Global variables
from plugins import queues, active_calls

async def main():
    await bot.start()
    await user.start()
    await call.start()
    
    print("✅ Bot started successfully!")
    print("✅ Assistant connected!")
    print("✅ Voice Chat ready!")
    print("=" * 50)
    
    # Import all command handlers
    from plugins import (
        play, pause, resume, skip, stop,
        queue_cmd, loop, shuffle, speed
    )
    
    # Register command handlers
    @bot.on_message(filters.command(["play"]))
    async def play_handler(client, message):
        await play(client, message, bot, user, call)
    
    @bot.on_message(filters.command(["pause"]))
    async def pause_handler(client, message):
        await pause(client, message, call)
    
    @bot.on_message(filters.command(["resume"]))
    async def resume_handler(client, message):
        await resume(client, message, call)
    
    @bot.on_message(filters.command(["skip"]))
    async def skip_handler(client, message):
        await skip(client, message, call)
    
    @bot.on_message(filters.command(["stop", "end"]))
    async def stop_handler(client, message):
        await stop(client, message, call)
    
    @bot.on_message(filters.command(["queue"]))
    async def queue_handler(client, message):
        await queue_cmd(client, message)
    
    @bot.on_message(filters.command(["loop"]))
    async def loop_handler(client, message):
        await loop(client, message)
    
    @bot.on_message(filters.command(["shuffle"]))
    async def shuffle_handler(client, message):
        await shuffle(client, message)
    
    @bot.on_message(filters.command(["speed"]))
    async def speed_handler(client, message):
        await speed(client, message, call)
    
    @bot.on_message(filters.command(["start", "help"]))
    async def start_handler(client, message):
        await message.reply(
            "🎵 **Fallen Music Bot**\n\n"
            "**Commands:**\n"
            "`/play` <song> - Play a song\n"
            "`/pause` - Pause playback\n"
            "`/resume` - Resume playback\n"
            "`/skip` - Skip current track\n"
            "`/stop` - Stop playback\n"
            "`/queue` - Show queue\n"
            "`/loop` - Toggle loop\n"
            "`/shuffle` - Shuffle queue\n"
            "`/speed` <0.5-2.0> - Change speed"
        )
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
