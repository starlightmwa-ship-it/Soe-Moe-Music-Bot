import asyncio
from pyrogram import Client, filters, idle
from config import API_ID, API_HASH, BOT_TOKEN, ASSISTANT_SESSION

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=ASSISTANT_SESSION)

@bot.on_message(filters.command(["start"]))
async def start_cmd(client, message):
    print(f"✅ /start from {message.from_user.id}")
    await message.reply("Bot is working!")

async def main():
    await bot.start()
    await assistant.start()
    print("Bot started!")
    await idle()

asyncio.run(main())
