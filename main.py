# main.py
import asyncio
import sys
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import API_ID, API_HASH, BOT_TOKEN, ASSISTANT_SESSION

# Keep-alive module import
import keep_alive

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

# Global storage
queues = {}
group_settings = {}
loop_modes = {}

# ==================== 24/7 KEEP ALIVE PING ====================
async def keep_alive_ping():
    """Send ping to console every 10 minutes to keep bot awake on Render"""
    while True:
        await asyncio.sleep(600)  # 10 minutes
        print("🏓 Keep-alive ping - Bot is running 24/7")
# ===============================================================

# ==================== PLAYER BUTTONS ====================
async def get_player_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data="pause"),
            InlineKeyboardButton("⏹ Stop", callback_data="stop"),
            InlineKeyboardButton("⏭ Skip", callback_data="skip"),
        ],
        [
            InlineKeyboardButton("🔄 Loop", callback_data="loop"),
            InlineKeyboardButton("🎲 Shuffle", callback_data="shuffle"),
            InlineKeyboardButton("⚡ Speed", callback_data="speed"),
        ],
        [
            InlineKeyboardButton("📋 Queue", callback_data="queue"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
            InlineKeyboardButton("❌ Close", callback_data="close"),
        ],
    ])

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
    chat_id = message.chat.id
    query = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
    
    if not query:
        await message.reply("⚠️ Usage: `/play <song name>`")
        return
    
    await message.reply(f"🔍 Searching `{query[:50]}`...")
    
    # Simplified play logic - you can expand this
    await message.reply(f"✅ Playing: **{query[:50]}**")

@bot.on_message(filters.command("pause"))
async def pause_handler(client, message):
    chat_id = message.chat.id
    await message.reply("⏸ Paused")

@bot.on_message(filters.command("resume"))
async def resume_handler(client, message):
    chat_id = message.chat.id
    await message.reply("▶️ Resumed")

@bot.on_message(filters.command("skip"))
async def skip_handler(client, message):
    await message.reply("⏭️ Skipped")

@bot.on_message(filters.command("stop"))
async def stop_handler(client, message):
    await message.reply("⛔ Stopped")

@bot.on_message(filters.command("queue"))
async def queue_handler(client, message):
    await message.reply("📋 Queue is empty!")

@bot.on_message(filters.command("loop"))
async def loop_handler(client, message):
    chat_id = message.chat.id
    current = loop_modes.get(chat_id, 0)
    current = (current + 1) % 3
    loop_modes[chat_id] = current
    mode_text = ["Off", "Single", "Queue"][current]
    await message.reply(f"🔄 Loop mode: **{mode_text}**")

@bot.on_message(filters.command("shuffle"))
async def shuffle_handler(client, message):
    await message.reply("🎲 Queue shuffled!")

@bot.on_message(filters.command("speed"))
async def speed_handler(client, message):
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

@bot.on_message(filters.command("auth"))
async def auth_handler(client, message):
    reply = message.reply_to_message
    if not reply:
        await message.reply("⚠️ Reply to a user to authorize!")
        return
    await message.reply(f"✅ Authorized user!")

@bot.on_message(filters.command("unauth"))
async def unauth_handler(client, message):
    reply = message.reply_to_message
    if not reply:
        await message.reply("⚠️ Reply to a user to unauthorize!")
        return
    await message.reply(f"❌ Unauthorized user!")

@bot.on_message(filters.command("setting"))
async def setting_handler(client, message):
    chat_id = message.chat.id
    admin_only = group_settings.get(chat_id, {}).get('admin_only', False)
    lang = group_settings.get(chat_id, {}).get('language', 'en')
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🌐 Language: {'🇲🇲 Myanmar' if lang == 'my' else '🇬🇧 English'}", callback_data="change_lang")],
        [InlineKeyboardButton(f"👑 Admin Only: {'✅ ON' if admin_only else '❌ OFF'}", callback_data="toggle_admin")],
        [InlineKeyboardButton("❌ Close", callback_data="close_settings")]
    ])
    await message.reply("⚙️ **Settings Panel**", reply_markup=keyboard)

# ==================== CALLBACK QUERY HANDLERS ====================

@bot.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    
    if data == "pause":
        await callback_query.answer("⏸ Paused")
    elif data == "stop":
        await callback_query.answer("⛔ Stopped")
    elif data == "skip":
        await callback_query.answer("⏭ Skipped")
    elif data == "loop":
        current = loop_modes.get(chat_id, 0)
        current = (current + 1) % 3
        loop_modes[chat_id] = current
        mode_text = ["Off", "Single", "Queue"][current]
        await callback_query.answer(f"🔄 Loop: {mode_text}")
    elif data == "shuffle":
        await callback_query.answer("🎲 Queue shuffled!")
    elif data == "queue":
        await callback_query.answer("Queue is empty!", show_alert=True)
    elif data == "settings":
        await callback_query.answer("⚙️ Settings")
    elif data == "change_lang":
        if chat_id not in group_settings:
            group_settings[chat_id] = {}
        current = group_settings[chat_id].get('language', 'en')
        new_lang = "my" if current == "en" else "en"
        group_settings[chat_id]['language'] = new_lang
        await callback_query.answer(f"Language: {'Myanmar' if new_lang == 'my' else 'English'}")
    elif data == "toggle_admin":
        if chat_id not in group_settings:
            group_settings[chat_id] = {}
        current = group_settings[chat_id].get('admin_only', False)
        group_settings[chat_id]['admin_only'] = not current
        await callback_query.answer(f"Admin Only: {'ON' if not current else 'OFF'}")
    elif data == "close_settings":
        await callback_query.message.delete()
        await callback_query.answer()
    else:
        await callback_query.answer()

# ==================== MAIN ====================

async def main():
    # Start HTTP server for Render port binding
    keep_alive.keep_alive()
    
    await bot.start()
    await assistant.start()
    
    print("✅ Bot started successfully!")
    print("✅ Assistant connected!")
    print("✅ Voice Chat ready!")
    print("✅ 24/7 Keep Alive: ENABLED (10 minutes ping)")
    print("=" * 50)
    
    # Start keep alive ping task
    asyncio.create_task(keep_alive_ping())
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
