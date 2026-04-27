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

# Initialize Bot and Assistant
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=ASSISTANT_SESSION)

# Global queue and settings storage
queues = {}
group_settings = {}
loop_modes = {}

# ==================== 24/7 KEEP ALIVE (10 minutes ping) ====================
async def keep_alive():
    """Send ping to console every 10 minutes to keep bot awake on Render"""
    while True:
        await asyncio.sleep(600)  # 10 minutes
        print("🏓 Keep-alive ping - Bot is running 24/7")
# ============================================================================

# ==================== HELPER FUNCTIONS ====================
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

async def check_admin(message):
    chat_id = message.chat.id
    if chat_id in group_settings and group_settings[chat_id].get('admin_only', False):
        member = await message.chat.get_member(message.from_user.id)
        if member.status not in ['administrator', 'creator']:
            await message.reply("⚠️ Admin only command!")
            return False
    return True

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
    if not await check_admin(message):
        return
    
    chat_id = message.chat.id
    query = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
    
    if not query:
        await message.reply("⚠️ Usage: `/play <song name>`")
        return
    
    await message.reply(f"🔍 Searching `{query[:50]}`...")
    
    # Import play function from plugins
    from plugins.play import play
    await play(client, message, bot, assistant, queues, group_settings)

@bot.on_message(filters.command("pause"))
async def pause_handler(client, message):
    if not await check_admin(message):
        return
    from plugins.pause import pause
    await pause(client, message, assistant, queues)

@bot.on_message(filters.command("resume"))
async def resume_handler(client, message):
    if not await check_admin(message):
        return
    from plugins.resume import resume
    await resume(client, message, assistant, queues)

@bot.on_message(filters.command("skip"))
async def skip_handler(client, message):
    if not await check_admin(message):
        return
    from plugins.skip import skip
    await skip(client, message, assistant, queues, bot)

@bot.on_message(filters.command("stop"))
async def stop_handler(client, message):
    if not await check_admin(message):
        return
    from plugins.stop import stop
    await stop(client, message, assistant, queues, bot)

@bot.on_message(filters.command("queue"))
async def queue_handler(client, message):
    from plugins.queue import queue_cmd
    await queue_cmd(client, message, queues)

@bot.on_message(filters.command("loop"))
async def loop_handler(client, message):
    if not await check_admin(message):
        return
    from plugins.loop import loop
    await loop(client, message, loop_modes)

@bot.on_message(filters.command("shuffle"))
async def shuffle_handler(client, message):
    if not await check_admin(message):
        return
    from plugins.shuffle import shuffle
    await shuffle(client, message, queues)

@bot.on_message(filters.command("speed"))
async def speed_handler(client, message):
    if not await check_admin(message):
        return
    from plugins.speed import speed
    await speed(client, message, assistant, queues)

@bot.on_message(filters.command("auth"))
async def auth_handler(client, message):
    if not await check_admin(message):
        return
    from plugins.auth import auth
    await auth(client, message, group_settings)

@bot.on_message(filters.command("unauth"))
async def unauth_handler(client, message):
    if not await check_admin(message):
        return
    from plugins.auth import unauth
    await unauth(client, message, group_settings)

@bot.on_message(filters.command("setting"))
async def setting_handler(client, message):
    from plugins.settings import setting
    await setting(client, message, group_settings)

# ==================== CALLBACK QUERY HANDLERS ====================

@bot.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    
    if data == "pause":
        if chat_id in queues and queues[chat_id]:
            await assistant.pause_stream(chat_id)
            await callback_query.answer("⏸ Paused")
    elif data == "stop":
        await assistant.leave_group_call(chat_id)
        if chat_id in queues:
            queues[chat_id].clear()
        await callback_query.answer("⛔ Stopped")
        await callback_query.message.delete()
    elif data == "skip":
        if chat_id in queues and queues[chat_id]:
            next_track = queues[chat_id].pop(0)
            await assistant.change_stream(chat_id, next_track['url'])
            await callback_query.answer("⏭ Skipped")
    elif data == "loop":
        current = loop_modes.get(chat_id, 0)
        current = (current + 1) % 3
        loop_modes[chat_id] = current
        mode_text = ["Off", "Single", "Queue"][current]
        await callback_query.answer(f"🔄 Loop: {mode_text}")
    elif data == "shuffle":
        if chat_id in queues and len(queues[chat_id]) > 1:
            import random
            random.shuffle(queues[chat_id])
            await callback_query.answer("🎲 Queue shuffled!")
    elif data == "queue":
        if chat_id not in queues or not queues[chat_id]:
            await callback_query.answer("Queue is empty!", show_alert=True)
        else:
            text = "**📋 MUSIC QUEUE**\n\n"
            for i, track in enumerate(queues[chat_id][:10], 1):
                text += f"`{i}. {track['title'][:45]}`\n"
            await callback_query.message.reply(text)
    elif data == "settings":
        admin_only = group_settings.get(chat_id, {}).get('admin_only', False)
        lang = group_settings.get(chat_id, {}).get('language', 'en')
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🌐 Language: {'🇲🇲 Myanmar' if lang == 'my' else '🇬🇧 English'}", callback_data="change_lang")],
            [InlineKeyboardButton(f"👑 Admin Only: {'✅ ON' if admin_only else '❌ OFF'}", callback_data="toggle_admin")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ])
        await callback_query.message.edit_reply_markup(reply_markup=keyboard)
    elif data == "change_lang":
        current = group_settings.get(chat_id, {}).get('language', 'en')
        new_lang = "my" if current == "en" else "en"
        if chat_id not in group_settings:
            group_settings[chat_id] = {}
        group_settings[chat_id]['language'] = new_lang
        await callback_query.answer(f"Language: {'Myanmar' if new_lang == 'my' else 'English'}")
    elif data == "toggle_admin":
        if chat_id not in group_settings:
            group_settings[chat_id] = {}
        current = group_settings[chat_id].get('admin_only', False)
        group_settings[chat_id]['admin_only'] = not current
        await callback_query.answer(f"Admin Only: {'ON' if not current else 'OFF'}")
    elif data == "back":
        await callback_query.message.edit_reply_markup(reply_markup=await get_player_buttons())
    elif data == "close":
        await callback_query.message.delete()
    else:
        await callback_query.answer()

# ==================== MAIN ====================

async def main():
    await bot.start()
    await assistant.start()
    
    print("✅ Bot started successfully!")
    print("✅ Assistant connected!")
    print("✅ Voice Chat ready!")
    print("✅ 24/7 Keep Alive: ENABLED (10 minutes ping)")
    print("=" * 50)
    
    # Start keep alive task
    asyncio.create_task(keep_alive())
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
