import asyncio
import os
from datetime import datetime
from threading import Thread
from typing import Dict, List

from telethon import TelegramClient, events
from telethon.tl.types import Message
from flask import Flask, jsonify
import yt_dlp
from pymongo import MongoClient
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioStream, InputStream, AudioPiped

# ---------- Environment Variables ----------
API_ID = int(os.environ.get("API_ID", 31427123))
API_HASH = os.environ.get("API_HASH", "27b540811ee6d2423f86a779848515ee")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8783739539:AAFPM95HIrSJQ-yoPtc-r8guZ-QJFgPymWA")
ASSISTANT_SESSION = os.environ.get("ASSISTANT_SESSION", "")
MONGO_URI = os.environ.get("MONGO_URI", "")
OWNER_ID = int(os.environ.get("OWNER_ID", 6904606472))
PORT = int(os.environ.get("PORT", 8080))

# ---------- Flask Web Server ----------
web_app = Flask(__name__)

@web_app.route('/')
@web_app.route('/health')
def health():
    return jsonify({"status": "alive", "timestamp": datetime.now().isoformat()})

def run_web():
    web_app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# ---------- Telegram Client ----------
bot = TelegramClient("MusicBot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
assistant = TelegramClient("Assistant", API_ID, API_HASH).start(session=ASSISTANT_SESSION)
call = PyTgCalls(assistant)

# ---------- MongoDB ----------
mongo_client = MongoClient(MONGO_URI) if MONGO_URI else None
db = mongo_client["music_bot"] if mongo_client else None

# ---------- Data ----------
queues: Dict[int, List[Dict]] = {}
now_playing: Dict[int, Dict] = {}

# ---------- Helper Functions ----------
async def get_audio_details(query: str, requester: str = ""):
    """YouTube ကနေ သီချင်းအချက်အလက် ထုတ်ယူမယ်"""
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
        
        # Audio URL ရှာမယ်
        audio_url = None
        if info.get('url'):
            audio_url = info['url']
        elif info.get('formats'):
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
            "requester": requester
        }

async def start_playback(chat_id: int):
    """Queue ထဲက သီချင်းကို စဖွင့်မယ်"""
    if chat_id not in queues or len(queues[chat_id]) == 0:
        return
    
    song = queues[chat_id].pop(0)
    now_playing[chat_id] = song
    
    try:
        # AudioStream ကို URL နဲ့ တိုက်ရိုက်ဖွင့်မယ်
        audio_stream = AudioPiped(song['url'])
        await call.join_group_call(
            chat_id,
            InputStream(audio_stream),
        )
        await bot.send_message(chat_id, f"**▶️ Now Playing**\n\n🎵 **{song['title'][:60]}**\n👤 {song['requester']}")
    except Exception as e:
        error_msg = str(e)[:100]
        await bot.send_message(chat_id, f"❌ **Playback Error:** {error_msg}")
        print(f"Playback error in {chat_id}: {e}")

# ---------- Command Handlers ----------
@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply("🎵 **Hello! Music Bot is Alive!**\nSend /play <song name> in groups")
    await asyncio.sleep(10)
    await event.delete()

@bot.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    text = """**📖 Commands:**
/play <name/link> - Play music
/pause - Pause playback
/resume - Resume playback
/skip - Skip current song
/end - Stop and clear queue
/queue - Show queue
/ping - Check bot status"""
    await event.reply(text)
    await asyncio.sleep(15)
    await event.delete()

@bot.on(events.NewMessage(pattern='/play(?: |$)(.*)'))
async def play_handler(event):
    chat_id = event.chat_id
    query = event.pattern_match.group(1).strip()
    
    if not query:
        await event.reply("❓ **Usage:** `/play song name` or `/play YouTube link`")
        await asyncio.sleep(5)
        await event.delete()
        return
    
    status_msg = await event.reply("🔍 **Searching on YouTube...**")
    
    song = await get_audio_details(query, event.sender.first_name)
    
    if not song.get('url'):
        await status_msg.edit("❌ **Song not found on YouTube!**")
        await asyncio.sleep(5)
        await status_msg.delete()
        await event.delete()
        return
    
    if chat_id not in queues:
        queues[chat_id] = []
    queues[chat_id].append(song)
    
    if chat_id not in now_playing:
        await status_msg.edit(f"▶️ **Now Playing:** {song['title'][:50]}")
        await start_playback(chat_id)
        await status_msg.delete()
    else:
        await status_msg.edit(f"✅ **Added to queue:** {song['title'][:50]}\n📍 Position: {len(queues[chat_id])}")
        await asyncio.sleep(10)
        await status_msg.delete()
    
    await asyncio.sleep(10)
    await event.delete()

@bot.on(events.NewMessage(pattern='/pause'))
async def pause_handler(event):
    try:
        await call.pause_stream(event.chat_id)
        await event.reply("⏸ **Paused**")
        await asyncio.sleep(5)
        await event.delete()
    except Exception as e:
        await event.reply(f"❌ {str(e)[:100]}")
        await asyncio.sleep(5)
        await event.delete()

@bot.on(events.NewMessage(pattern='/resume'))
async def resume_handler(event):
    try:
        await call.resume_stream(event.chat_id)
        await event.reply("▶️ **Resumed**")
        await asyncio.sleep(5)
        await event.delete()
    except Exception as e:
        await event.reply(f"❌ {str(e)[:100]}")
        await asyncio.sleep(5)
        await event.delete()

@bot.on(events.NewMessage(pattern='/skip'))
async def skip_handler(event):
    chat_id = event.chat_id
    try:
        await call.leave_group_call(chat_id)
        if chat_id in queues and len(queues[chat_id]) > 0:
            await start_playback(chat_id)
            await event.reply("⏭ **Skipped to next song**")
        else:
            now_playing.pop(chat_id, None)
            await event.reply("⏹ **Queue is empty, stopping...**")
        await asyncio.sleep(5)
        await event.delete()
    except Exception as e:
        await event.reply(f"❌ {str(e)[:100]}")
        await asyncio.sleep(5)
        await event.delete()

@bot.on(events.NewMessage(pattern='/end'))
async def end_handler(event):
    chat_id = event.chat_id
    try:
        await call.leave_group_call(chat_id)
        queues[chat_id] = []
        now_playing.pop(chat_id, None)
        await event.reply("🛑 **Stopped and cleared queue**")
        await asyncio.sleep(5)
        await event.delete()
    except Exception as e:
        await event.reply(f"❌ {str(e)[:100]}")
        await asyncio.sleep(5)
        await event.delete()

@bot.on(events.NewMessage(pattern='/queue'))
async def queue_handler(event):
    chat_id = event.chat_id
    if chat_id not in queues or len(queues[chat_id]) == 0:
        await event.reply("📋 **Queue is empty**")
    else:
        text = "**📋 Queue List:**\n\n"
        for i, song in enumerate(queues[chat_id][:10], 1):
            minutes = song['duration'] // 60
            seconds = song['duration'] % 60
            text += f"{i}. **{song['title'][:40]}** ({minutes}:{seconds:02d})\n"
        if len(queues[chat_id]) > 10:
            text += f"\n... and {len(queues[chat_id]) - 10} more"
        await event.reply(text)
    await asyncio.sleep(15)
    await event.delete()

@bot.on(events.NewMessage(pattern='/ping'))
async def ping_handler(event):
    start = datetime.now()
    msg = await event.reply("🏓 **Pong!**")
    end = datetime.now()
    latency = int((end - start).total_seconds() * 1000)
    await msg.edit(f"🏓 **Pong!**\n⏱ Latency: `{latency} ms`")
    await asyncio.sleep(10)
    await event.delete()

# ---------- Voice Chat Event ----------
@call.on_kicked()
@call.on_closed()
@call.on_left()
async def on_voice_end(chat_id: int):
    now_playing.pop(chat_id, None)

@call.on_stream_end()
async def on_stream_end(chat_id: int):
    now_playing.pop(chat_id, None)
    if chat_id in queues and len(queues[chat_id]) > 0:
        await start_playback(chat_id)
    else:
        await call.leave_group_call(chat_id)

# ---------- Main ----------
async def main():
    # Web server thread
    web_thread = Thread(target=run_web, daemon=True)
    web_thread.start()
    print(f"🌐 Web server started on port {PORT}")
    
    # Telegram clients
    print("Starting bot...")
    await bot.start()
    print("Starting assistant...")
    await assistant.start()
    print("Starting voice calls...")
    await call.start()
    
    print("\n✅ **Music Bot is RUNNING!**")
    print(f"🤖 Bot: @{(await bot.get_me()).username}")
    print(f"📡 Health check: http://localhost:{PORT}/health")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
