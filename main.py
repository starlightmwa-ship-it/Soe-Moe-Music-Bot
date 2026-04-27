# main.py
import asyncio
import sys
import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
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

# Initialize Bot and Assistant (Session file will be created automatically)
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=ASSISTANT_SESSION)

# Global storage
queues = {}
group_settings = {}
loop_modes = {}

# ==================== 24/7 KEEP ALIVE ====================
async def keep_alive():
    while True:
        await asyncio.sleep(600)
        print("🏓 Keep-alive ping - Bot is running 24/7")
# =========================================================

# ==================== COMMAND HANDLERS ====================
# (အဆင့်မြင့် command handlers များအတွက် လိုအပ်ပါက plugins ခွဲနိုင်သည်)

@bot.on_message(filters.command(["start", "help"]))
async def start_cmd(client, message):
    text = "🎵 **Soe Moe Music Bot**\n\n/play <song> - Play music\n/pause - Pause\n/resume - Resume\n/skip - Skip\n/stop - Stop\n/queue - Queue\n/loop - Loop\n/shuffle - Shuffle\n/speed - Speed"
    await message.reply(text)

# ==================== MAIN ====================
async def main():
    await bot.start()
    await assistant.start()
    print("✅ Bot and Assistant started!")
    asyncio.create_task(keep_alive())
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
