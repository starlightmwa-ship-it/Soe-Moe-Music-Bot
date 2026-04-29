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
    print(f"✅ /start received from {message.from_user.id}")
    await message.reply("🎵 Soe Moe Music Bot is alive! Send /play song_name")

@bot.on_message(filters.command("play"))
async def play_cmd(client, message):
    query = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
    if not query:
        await message.reply("⚠️ Usage: `/play <song name>`")
        return
    await message.reply(f"🔍 Searching: {query[:50]}...")
    await message.reply(f"✅ Playing: {query[:50]}")

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

# ==================== MAIN (အရေးကြီးဆုံးအပိုင်း) ====================

async def main():
    await bot.start()
    await assistant.start()
    
    print("✅ Bot started successfully!")
    print("✅ Assistant connected!")
    print("✅ Waiting for Telegram updates...")
    print("=" * 50)
    
    # ⚠️ ဒီစာကြောင်း ပါရမှာ အရေးကြီးဆုံးပါ
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
