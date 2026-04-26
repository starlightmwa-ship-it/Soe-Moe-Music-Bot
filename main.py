from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from assistant.userbot import app as userbot
from core.player import call, start_call

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def main():
    await bot.start()
    await userbot.start()
    await start_call()
    print("Bot Running...")

bot.run(main())
