import asyncio
import os
import re
from datetime import datetime
from threading import Thread
from typing import Dict, List
import asyncio

# Web Server
from flask import Flask, jsonify

# Telegram
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# Voice Chat
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioStream, InputStream
from pytgcalls.types.input_stream.audio import YouTubeAudio

# YouTube Download
import yt_dlp

# MongoDB
from pymongo import MongoClient

# Config
from config import (
    API_ID, API_HASH, BOT_TOKEN, ASSISTANT_SESSION,
    MONGO_URI, OWNER_ID, PORT
)

# ---------- MongoDB Setup (Queue & Settings သိမ်းဖို့) ----------
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["music_bot"]
queue_collection = db["queues"]
settings_collection = db["settings"]

# ---------- Flask Web Server (Render Keep-Alive အတွက်) ----------
web_app = Flask(__name__)

@web_app.route('/')
def index():
    return jsonify({
        "status": "alive",
        "bot": "Advanced Music Bot",
        "uptime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "groups": len(now_playing) if 'now_playing' in globals() else 0
    })

@web_app.route('/health')
def health():
    """UptimeRobot / cron-job.org စစ်ဆေးဖို့ endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "bot": "running"
    })

def run_web():
    """Flask web server ကို background thread မှာ run မယ်"""
    web_app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# ---------- Telegram Bot ----------
app = Client("MusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Assistant (Userbot) - Session String နဲ့
if ASSISTANT_SESSION:
    assistant = Client("Assistant", api_id=API_ID, api_hash=API_HASH, session_string=ASSISTANT_SESSION)
else:
    print("❌ ERROR: ASSISTANT_SESSION is required!")
    exit()

call = PyTgCalls(assistant)

# ---------- Global Data (In-memory cache) ----------
queues: Dict[int, List[Dict]] = {}
now_playing: Dict[int, Dict] = {}
loop_mode: Dict[int, bool] = {}

# ---------- Helper Functions ----------

async def load_settings(chat_id: int) -> Dict:
    """MongoDB ကနေ group setting တွေဖတ်မယ်"""
    data = settings_collection.find_one({"chat_id": chat_id})
    if not data:
        return {"lang": "my", "admin_only": False}
    return data

async def save_settings(chat_id: int, settings: Dict):
    """Group setting တွေ MongoDB မှာသိမ်းမယ်"""
    settings_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"chat_id": chat_id, **settings}},
        upsert=True
    )

async def get_audio_details(query: str, requester: str = None):
    """YouTube ကနေ သီချင်းအချက်အလက် ထုတ်ယူခြင်း"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    # URL မဟုတ်ရင် search
    if not (query.startswith("http://") or query.startswith("https://")):
        query = f"ytsearch:{query}"
    
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False))
        if 'entries' in info:
            info = info['entries'][0]
        
        # Duration ကို စက္ကန့်နဲ့ ရယူမယ်
        duration = info.get('duration', 0)
        if isinstance(duration, dict):
            duration = duration.get('seconds', 0)
        
        # Best audio stream URL ရယူမယ်
        audio_url = None
        if 'url' in info:
            audio_url = info['url']
        elif 'formats' in info:
            for f in info['formats']:
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    audio_url = f['url']
                    break
        
        return {
            "title": info.get('title', 'Unknown'),
            "duration": duration,
            "url": audio_url,
            "webpage_url": info.get('webpage_url', ''),
            "thumbnail": info.get('thumbnail', ''),
            "requester": requester or "Unknown"
        }

async def delete_delay(message: Message, delay: int = 10):
    """10 စက္ကန့်ကြာရင် မက်ဆေ့ချ်ကိုဖျက်မယ်"""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass

def get_player_buttons(chat_id: int, is_playing: bool = True):
    """Player UI Buttons"""
    buttons = [
        [
            InlineKeyboardButton("⏸ Pause" if is_playing else "▶️ Resume", callback_data=f"pause_{chat_id}"),
            InlineKeyboardButton("⏹ Stop", callback_data=f"end_{chat_id}"),
            InlineKeyboardButton("⏭ Skip", callback_data=f"skip_{chat_id}"),
        ],
        [
            InlineKeyboardButton("🔁 Loop", callback_data=f"loop_{chat_id}"),
            InlineKeyboardButton("🔀 Shuffle", callback_data=f"shuffle_{chat_id}"),
            InlineKeyboardButton("⚙️ Setting", callback_data=f"settings_{chat_id}"),
        ],
        [
            InlineKeyboardButton("📋 Queue", callback_data=f"queue_{chat_id}"),
            InlineKeyboardButton("🎧 Speed", callback_data=f"speed_{chat_id}"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)

async def send_playing_message(chat_id: int, song: Dict):
    """သီချင်းစဖွင့်ချိန် Thumbnail နဲ့ Button ပါတဲ့ Message ပို့ခြင်း"""
    thumbnail = song.get('thumbnail')
    duration_min = song['duration'] // 60
    duration_sec = song['duration'] % 60
    text = f"""**▶️ Now Playing**

🎵 **{song['title'][:50]}**
⏱ Duration: `{duration_min}:{duration_sec:02d}`
👤 Request: {song['requester']}"""
    
    try:
        if thumbnail and thumbnail.startswith("http"):
            await app.send_photo(chat_id, photo=thumbnail, caption=text, reply_markup=get_player_buttons(chat_id))
        else:
            await app.send_message(chat_id, text, reply_markup=get_player_buttons(chat_id))
    except Exception as e:
        print(f"Send playing message error: {e}")
        await app.send_message(chat_id, text, reply_markup=get_player_buttons(chat_id))

async def start_playback(chat_id: int):
    """Queue ထဲက သီချင်းကိုစဖွင့်မယ်"""
    if loop_mode.get(chat_id, False) and chat_id in now_playing:
        # Loop mode ဆိုရင် အသံဖိုင်ပြန်သုံးမယ်
        song = now_playing[chat_id]
    elif chat_id in queues and len(queues[chat_id]) > 0:
        song = queues[chat_id].pop(0)
        now_playing[chat_id] = song
    else:
        return
    
    try:
        # Stream စတင်ခြင်း
        if song.get('url'):
            audio_stream = YouTubeAudio(song['url'])
            await call.join_group_call(
                chat_id,
                InputStream(audio_stream),
            )
            await send_playing_message(chat_id, song)
    except Exception as e:
        print(f"Start playback error: {e}")
        await app.send_message(chat_id, f"❌ **Error:** {str(e)[:100]}")

# ---------- Commands ----------

@app.on_message(filters.command(["start"]) & filters.private)
async def start_command(client: Client, message: Message):
    await message.reply_text("🎵 **ဟိုင်း! ကျွန်တော် Advanced Music Bot ပါ**\n\n/song နဲ့ သီချင်းရှာပါ\nGroup ထဲမှာ /play နဲ့ သီချင်းဖွင့်ပါ")
    await delete_delay(message, 10)

@app.on_message(filters.command(["help"]))
async def help_command(client: Client, message: Message):
    text = """**📖 Command List**

**🎵 Playback:**
/play [နာမည်/link] - သီချင်းဖွင့်မယ်
/pause - ခဏရပ်မယ်
/resume - ပြန်ဖွင့်မယ်
/skip - နောက်တစ်ပုဒ်သွားမယ်
/end - ဖွင့်တာရပ်မယ်

**📋 Queue:**
/queue - တန်းစီထားတဲ့စာရင်း

**⚙️ Settings:**
/setting - Setting များ"""
    await message.reply_text(text)
    await delete_delay(message, 15)

@app.on_message(filters.command(["play"]) & filters.group)
async def play_command(client: Client, message: Message):
    chat_id = message.chat.id
    
    if len(message.command) < 2:
        await message.reply_text("❓ **Usage:** `/play သီချင်းနာမည်` or `/play YouTube link`")
        await delete_delay(message, 10)
        return
    
    query = " ".join(message.command[1:])
    status_msg = await message.reply_text("🔍 **YouTube မှာ ရှာနေပါတယ်...**")
    
    # သီချင်းအချက်အလက်ရယူမယ်
    song = await get_audio_details(query, message.from_user.first_name)
    
    if not song.get('url'):
        await status_msg.edit_text("❌ **YouTube မှာ ရှာမတွေ့ပါဘူး**")
        await asyncio.sleep(5)
        await status_msg.delete()
        await delete_delay(message, 10)
        return
    
    # Queue ထဲထည့်မယ်
    if chat_id not in queues:
        queues[chat_id] = []
    queues[chat_id].append(song)
    
    # ရှေ့ဆုံးသီချင်းမဖွင့်ရသေးရင် စဖွင့်မယ်
    if chat_id not in now_playing:
        await status_msg.edit_text(f"✅ **Queue ထဲထည့်ပြီး စဖွင့်ပါမယ်...**\n🎵 {song['title'][:50]}")
        await start_playback(chat_id)
        await status_msg.delete()
    else:
        await status_msg.edit_text(f"✅ **Queue ထဲထည့်လိုက်ပါပြီ**\n🎵 {song['title'][:50]}\n📍 Position: {len(queues[chat_id])}")
        await delete_delay(status_msg, 10)
    
    await delete_delay(message, 10)

@app.on_message(filters.command(["pause"]) & filters.group)
async def pause_command(client: Client, message: Message):
    try:
        await call.pause_stream(message.chat.id)
        await message.reply_text("⏸ **Paused**")
        await delete_delay(message, 10)
    except Exception as e:
        await message.reply_text(f"❌ {str(e)[:100]}")
        await delete_delay(message, 10)

@app.on_message(filters.command(["resume"]) & filters.group)
async def resume_command(client: Client, message: Message):
    try:
        await call.resume_stream(message.chat.id)
        await message.reply_text("▶️ **Resumed**")
        await delete_delay(message, 10)
    except Exception as e:
        await message.reply_text(f"❌ {str(e)[:100]}")
        await delete_delay(message, 10)

@app.on_message(filters.command(["skip"]) & filters.group)
async def skip_command(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        await call.stop_stream(chat_id)
        if chat_id in queues and len(queues[chat_id]) > 0:
            await start_playback(chat_id)
            await message.reply_text("⏭ **Skipped ➡️ နောက်သီချင်း**")
        else:
            if chat_id in now_playing:
                del now_playing[chat_id]
            await message.reply_text("⏹ **Queue ကုန်ပါပြီ**")
    except Exception as e:
        await message.reply_text(f"❌ {str(e)[:100]}")
    await delete_delay(message, 10)

@app.on_message(filters.command(["end", "stop"]) & filters.group)
async def end_command(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        await call.leave_group_call(chat_id)
        if chat_id in queues:
            queues[chat_id].clear()
        if chat_id in now_playing:
            del now_playing[chat_id]
        await message.reply_text("🛑 **Stopped and left voice chat**")
    except Exception as e:
        await message.reply_text(f"❌ {str(e)[:100]}")
    await delete_delay(message, 10)

@app.on_message(filters.command(["queue"]) & filters.group)
async def queue_command(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id not in queues or len(queues[chat_id]) == 0:
        await message.reply_text("📋 **Queue ထဲမှာ သီချင်းမရှိပါဘူး**")
    else:
        text = "**📋 Queue List**\n\n"
        for i, song in enumerate(queues[chat_id][:10], 1):
            text += f"{i}. {song['title'][:40]}\n"
        if len(queues[chat_id]) > 10:
            text += f"\n...နဲ့ {len(queues[chat_id]) - 10} ပုဒ်ထပ်ရှိသေးတယ်"
        await message.reply_text(text)
    await delete_delay(message, 15)

@app.on_message(filters.command(["ping"]))
async def ping_command(client: Client, message: Message):
    start = datetime.now()
    msg = await message.reply_text("🏓 **Pong!**")
    end = datetime.now()
    latency = int((end - start).total_seconds() * 1000)
    await msg.edit_text(f"🏓 **Pong!**\n⏱ Latency: `{latency} ms`")
    await delete_delay(msg, 10)
    await delete_delay(message, 10)

@app.on_message(filters.command(["song"]) & filters.private)
async def song_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❓ **Usage:** `/song သီချင်းနာမည်`")
        return
    
    query = " ".join(message.command[1:])
    msg = await message.reply_text("🔍 **Searching...**")
    song = await get_audio_details(query)
    await msg.delete()
    
    if song.get('webpage_url'):
        await message.reply_text(f"🎵 **Found:** {song['title'][:100]}\n🔗 {song['webpage_url']}")
    else:
        await message.reply_text(f"🎵 **Found:** {song['title'][:100]}")
    await delete_delay(message, 10)

@app.on_message(filters.command(["setting"]) & filters.group)
async def setting_command(client: Client, message: Message):
    chat_id = message.chat.id
    
    # Admin စစ်ဆေးခြင်း
    user = await message.chat.get_member(message.from_user.id)
    if user.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await message.reply_text("🚫 **Admins only can change settings!**")
        await delete_delay(message, 10)
        return
    
    settings = await load_settings(chat_id)
    lang_text = "🇲🇲 Myanmar" if settings['lang'] == 'my' else "🇬🇧 English"
    admin_text = "🔒 ON" if settings['admin_only'] else "🔓 OFF"
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🌐 Language: {lang_text}", callback_data=f"lang_{chat_id}")],
        [InlineKeyboardButton(f"👑 Admin Only: {admin_text}", callback_data=f"admin_{chat_id}")],
        [InlineKeyboardButton("❌ Close", callback_data=f"close_{chat_id}")]
    ])
    
    await message.reply_text("**⚙️ Bot Settings**", reply_markup=buttons)
    await delete_delay(message, 30)

# ---------- Callback Handlers ----------
@app.on_callback_query()
async def callback_handler(client: Client, callback: CallbackQuery):
    data = callback.data
    chat_id = callback.message.chat.id
    
    if data.startswith("pause_"):
        await call.pause_stream(chat_id)
        await callback.answer("⏸ Paused")
    elif data.startswith("end_"):
        await call.leave_group_call(chat_id)
        if chat_id in queues:
            queues[chat_id].clear()
        if chat_id in now_playing:
            del now_playing[chat_id]
        await callback.answer("🛑 Stopped")
        await callback.message.delete()
    elif data.startswith("skip_"):
        await call.stop_stream(chat_id)
        await callback.answer("⏭ Skipped")
    elif data.startswith("loop_"):
        loop_mode[chat_id] = not loop_mode.get(chat_id, False)
        status = "ON" if loop_mode[chat_id] else "OFF"
        await callback.answer(f"🔁 Loop {status}")
    elif data.startswith("lang_"):
        settings = await load_settings(chat_id)
        settings['lang'] = 'en' if settings['lang'] == 'my' else 'my'
        await save_settings(chat_id, settings)
        await callback.answer(f"Language: {'English' if settings['lang'] == 'en' else 'Myanmar'}")
        await callback.message.delete()
        await setting_command(client, callback.message)
    elif data.startswith("admin_"):
        settings = await load_settings(chat_id)
        settings['admin_only'] = not settings['admin_only']
        await save_settings(chat_id, settings)
        status = "ON" if settings['admin_only'] else "OFF"
        await callback.answer(f"Admin Only Mode: {status}")
        await callback.message.delete()
        await setting_command(client, callback.message)
    elif data.startswith("close_"):
        await callback.message.delete()
        await callback.answer("Closed")
    elif data.startswith("queue_"):
        await queue_command(client, callback.message)
    else:
        await callback.answer("Processing...")

# ---------- PyTgCalls Events ----------
@call.on_stream_end()
async def on_stream_end(chat_id: int):
    """သီချင်းပြီးသွားရင် နောက်တစ်ပုဒ်စဖွင့်မယ်"""
    if chat_id in now_playing:
        del now_playing[chat_id]
    
    if loop_mode.get(chat_id, False):
        await start_playback(chat_id)
    elif chat_id in queues and len(queues[chat_id]) > 0:
        await start_playback(chat_id)
    else:
        await call.leave_group_call(chat_id)

# ---------- Main Entry ----------
async def main():
    # Web server ကို background thread မှာ run မယ်
    web_thread = Thread(target=run_web, daemon=True)
    web_thread.start()
    print("🌐 Web server started on port", PORT)
    
    # Assistant စတင်မယ်
    await assistant.start()
    print("📱 Assistant started")
    
    # Bot စတင်မယ်
    await app.start()
    print("🤖 Bot started")
    
    # Voice Chat စတင်မယ်
    await call.start()
    print("🎵 Voice chat started")
    
    print("\n✅ **Music Bot is RUNNING!**")
    print(f"📡 Web: http://localhost:{PORT}")
    print("🏓 Keep-alive: 10 min ping required")
    
    # Bot ကို အဆုံးမသတ်အောင် အမြဲ run နေဖို့
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
