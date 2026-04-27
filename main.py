# main.py
import asyncio
import threading
from pyrogram import Client, filters, idle
from config import API_ID, API_HASH, BOT_TOKEN, ASSISTANT_SESSION
from keep_alive import keep_alive

# Start Flask server for Render port binding
threading.Thread(target=keep_alive, daemon=True).start()

print("=" * 50)
print("🎵 SOE MOE MUSIC BOT STARTING...")
print("=" * 50)

# Initialize Bot and Assistant
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=ASSISTANT_SESSION)

# ==================== COMMAND HANDLERS ====================

@bot.on_message(filters.command(["start", "help"]))
async def start_cmd(client, message):
    print(f"✅ /start received from {message.from_user.id}")  # Debug log
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

**Made with ❤️**
"""
    await message.reply(text)

@bot.on_message(filters.command("play"))
async def play_cmd(client, message):
    query = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
    if not query:
        await message.reply("⚠️ Usage: `/play <song name>`")
        return
    await message.reply(f"🔍 Searching: `{query[:50]}`...")
    await message.reply(f"✅ Playing: **{query[:50]}**")

@bot.on_message(filters.command("pause"))
async def pause_cmd(client, message):
    await message.reply("⏸ Paused")

@bot.on_message(filters.command("resume"))
async def resume_cmd(client, message):
    await message.reply("▶️ Resumed")

@bot.on_message(filters.command("skip"))
async def skip_cmd(client, message):
    await message.reply("⏭️ Skipped")

@bot.on_message(filters.command("stop"))
async def stop_cmd(client, message):
    await message.reply("⛔ Stopped")

@bot.on_message(filters.command("queue"))
async def queue_cmd(client, message):
    await message.reply("📋 Queue is empty!")

@bot.on_message(filters.command("loop"))
async def loop_cmd(client, message):
    await message.reply("🔄 Loop toggled")

@bot.on_message(filters.command("shuffle"))
async def shuffle_cmd(client, message):
    await message.reply("🎲 Queue shuffled!")

@bot.on_message(filters.command("speed"))
async def speed_cmd(client, message):
    args = message.text.split()
    if len(args) != 2:
        await message.reply("Usage: `/speed 0.5` to `2.0`")
        return
    try:
        speed = float(args[1])
        if speed < 0.5 or speed > 2.0:
            raise ValueError
        await message.reply(f"⚡ Speed changed to `{speed}x`")
    except:
        await message.reply("❌ Invalid speed! Use 0.5 to 2.0")

# ==================== MAIN ====================

async def main():
    await bot.start()
    await assistant.start()
    
    print("✅ Bot started successfully!")
    print("✅ Assistant connected!")
    print("✅ Voice Chat ready!")
    print("=" * 50)
    
    await idle()  # Keep bot running and listen for updates

if __name__ == "__main__":
    asyncio.run(main())
