import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from assistant.userbot import app as userbot
from core.player import start_call
from keep_alive import keep_alive
from core.ping import auto_ping

# ✅ Plugin loader important
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

async def main():
    # 🌐 keep alive server
    keep_alive()

    # 🤖 start bot + assistant
    await bot.start()
    await userbot.start()
    await start_call()

    # 📡 auto ping
    asyncio.create_task(auto_ping())

    print("✅ Music Bot Running...")

bot.run(main())
