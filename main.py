import asyncio
import os
from datetime import datetime
from threading import Thread
from typing import Dict, List

from telethon import TelegramClient, events
from telethon.tl.types import Message
from telethon.utils import get_input_location
from flask import Flask, jsonify
import yt_dlp
from pymongo import MongoClient
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioStream, InputStream
from pytgcalls.types.input_stream.audio import YouTubeAudio

from config import (
    API_ID, API_HASH, BOT_TOKEN, ASSISTANT_SESSION,
    MONGO_URI, OWNER_ID, PORT
)

# ---------- Flask Web Server ----------
web_app = Flask(__name__)

@web_app.route('/')
@web_app.route('/health')
def health():
    return jsonify({"status": "alive", "timestamp": datetime.now().isoformat()})

def run_web():
    web_app.run(host='0.0.0.0', port=PORT, debug=False)

# ---------- Telegram Bot (Telethon) ----------
bot = TelegramClient("MusicBot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Assistant (Userbot)
assistant = TelegramClient("Assistant", API_ID, API_HASH).start(session=ASSISTANT_SESSION)
call = PyTgCalls(assistant)

# ---------- MongoDB ----------
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["music_bot"]
queue_collection = db["queues"]
settings_collection = db["settings"]

# ---------- Global Data ----------
queues: Dict[int, List[Dict]] = {}
now_playing: Dict[int, Dict] = {}
loop_mode: Dict[int, bool] = {}

# ---------- Helper Functions ----------
async def get_audio_details(query: str, requester: str = None):
    """YouTube ကနေ သီချင်းအချက်အလက် ထုတ်ယူခြင်း"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }
    if not (query.startswith("http://") or query.startswith("https://")):
        query = f"ytsearch:{query}"
    
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False))
        if 'entries' in info:
            info = info['entries'][0]
        
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
            "duration": info.get('duration', 0),
            "url": audio_url,
            "webpage_url": info.get('webpage_url', ''),
            "thumbnail": info.get('thumbnail', ''),
            "requester": requester or "Unknown"
        }

async def delete_delay(message, delay: int = 10):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass

async def send_playing_message(chat_id: int, song: Dict):
    duration_min = song['duration'] // 60
    duration_sec = song['duration'] % 60
    text = f"**▶️ Now Playing**\n\n🎵 **{song['title'][:50]}**\n⏱ `{duration_min}:{duration_sec:02d}`\n👤 {song['requester']}"
    try:
        if song.get('thumbnail'):
            await bot.send_file(chat_id, song['thumbnail'], caption=text)
        else:
            await bot.send_message(chat_id, text)
    except:
        await bot.send_message(chat_id, text)

async def start_playback(chat_id: int):
    if loop_mode.get(chat_id, False) and chat_id in now_playing:
        song = now_playing[chat_id]
    elif chat_id in queues and len(queues[chat_id]) > 0:
        song = queues[chat_id].pop(0)
        now_playing[chat_id] = song
    else:
        return
    
    try:
        await call.join_group_call(
            chat_id,
            InputStream(YouTubeAudio(song['url'])),
        )
        await send_playing_message(chat_id, song)
    except Exception as e:
        print(f"Playback error: {e}")

# ---------- Bot Commands ----------
@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply("🎵 **Hello! I'm Advanced Music Bot**\nSend /help for commands")
    await delete_delay(event.message, 10)

@bot.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    text = """**📖 Commands:**

/play [name/link] - Play song
/pause - Pause
/resume - Resume
/skip - Skip
/end - Stop
/queue - Show queue
/ping - Check status
/setting - Settings (admins only)"""
    await event.reply(text)
    await delete_delay(event.message, 15)

@bot.on(events.NewMessage(pattern='/play(?: |$)(.*)'))
async def play_handler(event):
    chat_id = event.chat_id
    query = event.pattern_match.group(1).strip()
    
    if not query:
        await event.reply("❓ Usage: `/play song name`")
        await delete_delay(event.message, 10)
        return
    
    status_msg = await event.reply("🔍 **Searching on YouTube...**")
    
    song = await get_audio_details(query, event.sender.first_name)
    
    if not song.get('url'):
        await status_msg.edit("❌ **Song not found!**")
        await asyncio.sleep(5)
        await status_msg.delete()
        return
    
    if chat_id not in queues:
        queues[chat_id] = []
    queues[chat_id].append(song)
    
    if chat_id not in now_playing:
        await status_msg.edit(f"✅ **Playing:** {song['title'][:50]}")
        await start_playback(chat_id)
        await status_msg.delete()
    else:
        await status_msg.edit(f"✅ **Added to queue:** {song['title'][:50]}\n📍 Position: {len(queues[chat_id])}")
        await delete_delay(status_msg, 10)
    
    await delete_delay(event.message, 10)

@bot.on(events.NewMessage(pattern='/pause'))
async def pause_handler(event):
    try:
        await call.pause_stream(event.chat_id)
        await event.reply("⏸ **Paused**")
        await delete_delay(event.message, 10)
    except Exception as e:
        await event.reply(f"❌ {str(e)[:100]}")

@bot.on(events.NewMessage(pattern='/resume'))
async def resume_handler(event):
    try:
        await call.resume_stream(event.chat_id)
        await event.reply("▶️ **Resumed**")
        await delete_delay(event.message, 10)
    except Exception as e:
        await event.reply(f"❌ {str(e)[:100]}")

@bot.on(events.NewMessage(pattern='/skip'))
async def skip_handler(event):
    chat_id = event.chat_id
    try:
        await call.stop_stream(chat_id)
        if chat_id in queues and len(queues[chat_id]) > 0:
            await start_playback(chat_id)
            await event.reply("⏭ **Skipped**")
        else:
            if chat_id in now_playing:
                del now_playing[chat_id]
            await event.reply("⏹ **Queue empty**")
    except Exception as e:
        await event.reply(f"❌ {str(e)[:100]}")
    await delete_delay(event.message, 10)

@bot.on(events.NewMessage(pattern='/end'))
async def end_handler(event):
    chat_id = event.chat_id
    try:
        await call.leave_group_call(chat_id)
        queues[chat_id] = []
        if chat_id in now_playing:
            del now_playing[chat_id]
        await event.reply("🛑 **Stopped**")
    except Exception as e:
        await event.reply(f"❌ {str(e)[:100]}")
    await delete_delay(event.message, 10)

@bot.on(events.NewMessage(pattern='/queue'))
async def queue_handler(event):
    chat_id = event.chat_id
    if chat_id not in queues or len(queues[chat_id]) == 0:
        await event.reply("📋 **Queue is empty**")
    else:
        text = "**📋 Queue:**\n\n"
        for i, song in enumerate(queues[chat_id][:10], 1):
            text += f"{i}. {song['title'][:40]}\n"
        await event.reply(text)
    await delete_delay(event.message, 15)

@bot.on(events.NewMessage(pattern='/ping'))
async def ping_handler(event):
    start = datetime.now()
    msg = await event.reply("🏓 **Pong!**")
    end = datetime.now()
    latency = int((end - start).total_seconds() * 1000)
    await msg.edit(f"🏓 **Pong!**\n⏱ Latency: `{latency} ms`")
    await delete_delay(msg, 10)
    await delete_delay(event.message, 10)

# ---------- Voice Chat Events ----------
@call.on_stream_end()
async def on_stream_end(chat_id: int):
    if chat_id in now_playing:
        del now_playing[chat_id]
    
    if loop_mode.get(chat_id, False):
        await start_playback(chat_id)
    elif chat_id in queues and len(queues[chat_id]) > 0:
        await start_playback(chat_id)
    else:
        await call.leave_group_call(chat_id)

# ---------- Main ----------
async def main():
    # Web thread
    web_thread = Thread(target=run_web, daemon=True)
    web_thread.start()
    
    print("Starting bot...")
    await bot.start()
    print("Starting assistant...")
    await assistant.start()
    print("Starting voice calls...")
    await call.start()
    
    print("\n✅ **Bot is running!**")
    print(f"🌐 Web: http://localhost:{PORT}")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
