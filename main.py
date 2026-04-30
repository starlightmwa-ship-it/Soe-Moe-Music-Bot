import asyncio
import os
from datetime import datetime
from threading import Thread
from typing import Dict, List

from pyrogram import Client, filters
from pyrogram.types import Message
from flask import Flask, jsonify
import yt_dlp
from pymongo import MongoClient

# PyTgCalls 5.0.0 အတွက် import ပြင်ဆင်ချက်
import pytgcalls
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioStream, InputStream
from pytgcalls.types.input_stream.audio import YouTubeAudio

# ---------- Config ----------
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

# ---------- Telegram Clients ----------
app = Client("MusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("Assistant", api_id=API_ID, api_hash=API_HASH, session_string=ASSISTANT_SESSION)
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
    
    if not (query.startswith("http://") or query.startswith("https://")):
        query = f"ytsearch:{query}"
    
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False))
        if 'entries' in info:
            info = info['entries'][0]
        
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
        print(f"Starting playback in {chat_id}: {song['title']}")
        await call.join_group_call(
            chat_id,
            InputStream(
                YouTubeAudio(
                    song['url'],
                    audio_parameters=None,
                )
            ),
        )
        duration_min = song['duration'] // 60
        duration_sec = song['duration'] % 60
        text = f"**▶️ Now Playing**\n\n🎵 **{song['title'][:60]}**\n⏱ `{duration_min}:{duration_sec:02d}`\n👤 {song['requester']}"
        
        if song.get('thumbnail'):
            await app.send_photo(chat_id, song['thumbnail'], caption=text)
        else:
            await app.send_message(chat_id, text)
            
    except Exception as e:
        error_msg = str(e)[:100]
        print(f"Playback error in {chat_id}: {e}")
        await app.send_message(chat_id, f"❌ **Error:** {error_msg}")

# ---------- Bot Commands ----------
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(_, message: Message):
    await message.reply("🎵 **Music Bot is Alive!**\nAdd me to group and use /play")
    await asyncio.sleep(10)
    try:
        await message.delete()
    except:
        pass

@app.on_message(filters.command("help"))
async def help_cmd(_, message: Message):
    text = """**📖 Commands:**

/play <name/link> - Play music
/pause - Pause playback  
/resume - Resume playback
/skip - Skip current song
/end - Stop and clear queue
/queue - Show queue
/ping - Check bot status"""
    await message.reply(text)
    await asyncio.sleep(15)
    try:
        await message.delete()
    except:
        pass

@app.on_message(filters.command("play") & filters.group)
async def play_cmd(_, message: Message):
    chat_id = message.chat.id
    
    if len(message.command) < 2:
        await message.reply("❓ **Usage:** `/play song name`")
        await asyncio.sleep(5)
        try:
            await message.delete()
        except:
            pass
        return
    
    query = " ".join(message.command[1:])
    status_msg = await message.reply("🔍 **Searching on YouTube...**")
    
    song = await get_audio_details(query, message.from_user.first_name)
    
    if not song.get('url'):
        await status_msg.edit("❌ **Song not found!**")
        await asyncio.sleep(5)
        try:
            await status_msg.delete()
            await message.delete()
        except:
            pass
        return
    
    if chat_id not in queues:
        queues[chat_id] = []
    queues[chat_id].append(song)
    
    if chat_id not in now_playing:
        await status_msg.edit(f"▶️ **Playing:** {song['title'][:50]}")
        await start_playback(chat_id)
        try:
            await status_msg.delete()
        except:
            pass
    else:
        await status_msg.edit(f"✅ **Added to queue:** {song['title'][:50]}\n📍 Position: {len(queues[chat_id])}")
        await asyncio.sleep(10)
        try:
            await status_msg.delete()
        except:
            pass
    
    await asyncio.sleep(10)
    try:
        await message.delete()
    except:
        pass

@app.on_message(filters.command("pause") & filters.group)
async def pause_cmd(_, message: Message):
    try:
        await call.pause_stream(message.chat.id)
        await message.reply("⏸ **Paused**")
        await asyncio.sleep(5)
        try:
            await message.delete()
        except:
            pass
    except Exception as e:
        await message.reply(f"❌ {str(e)[:100]}")
        await asyncio.sleep(5)
        try:
            await message.delete()
        except:
            pass

@app.on_message(filters.command("resume") & filters.group)
async def resume_cmd(_, message: Message):
    try:
        await call.resume_stream(message.chat.id)
        await message.reply("▶️ **Resumed**")
        await asyncio.sleep(5)
        try:
            await message.delete()
        except:
            pass
    except Exception as e:
        await message.reply(f"❌ {str(e)[:100]}")
        await asyncio.sleep(5)
        try:
            await message.delete()
        except:
            pass

@app.on_message(filters.command("skip") & filters.group)
async def skip_cmd(_, message: Message):
    chat_id = message.chat.id
    try:
        await call.leave_group_call(chat_id)
        if chat_id in queues and len(queues[chat_id]) > 0:
            await start_playback(chat_id)
            await message.reply("⏭ **Skipped to next song**")
        else:
            now_playing.pop(chat_id, None)
            await message.reply("⏹ **Queue empty, stopping...**")
        await asyncio.sleep(5)
        try:
            await message.delete()
        except:
            pass
    except Exception as e:
        await message.reply(f"❌ {str(e)[:100]}")
        await asyncio.sleep(5)
        try:
            await message.delete()
        except:
            pass

@app.on_message(filters.command("end") & filters.group)
async def end_cmd(_, message: Message):
    chat_id = message.chat.id
    try:
        await call.leave_group_call(chat_id)
        queues[chat_id] = []
        now_playing.pop(chat_id, None)
        await message.reply("🛑 **Stopped and cleared queue**")
        await asyncio.sleep(5)
        try:
            await message.delete()
        except:
            pass
    except Exception as e:
        await message.reply(f"❌ {str(e)[:100]}")
        await asyncio.sleep(5)
        try:
            await message.delete()
        except:
            pass

@app.on_message(filters.command("queue") & filters.group)
async def queue_cmd(_, message: Message):
    chat_id = message.chat.id
    if chat_id not in queues or len(queues[chat_id]) == 0:
        await message.reply("📋 **Queue is empty**")
    else:
        text = "**📋 Queue List:**\n\n"
        for i, song in enumerate(queues[chat_id][:10], 1):
            minutes = song['duration'] // 60
            seconds = song['duration'] % 60
            text += f"{i}. **{song['title'][:40]}** ({minutes}:{seconds:02d})\n"
        if len(queues[chat_id]) > 10:
            text += f"\n... and {len(queues[chat_id]) - 10} more"
        await message.reply(text)
    await asyncio.sleep(15)
    try:
        await message.delete()
    except:
        pass

@app.on_message(filters.command("ping"))
async def ping_cmd(_, message: Message):
    start = datetime.now()
    msg = await message.reply("🏓 **Pong!**")
    end = datetime.now()
    latency = int((end - start).total_seconds() * 1000)
    await msg.edit(f"🏓 **Pong!**\n⏱ Latency: `{latency} ms`")
    await asyncio.sleep(10)
    try:
        await message.delete()
    except:
        pass

# ---------- Voice Chat Events ----------
@call.on_stream_end()
async def on_stream_end(chat_id: int):
    """သီချင်းပြီးသွားရင် နောက်တစ်ပုဒ် ဖွင့်မယ်"""
    print(f"Stream ended in {chat_id}")
    now_playing.pop(chat_id, None)
    if chat_id in queues and len(queues[chat_id]) > 0:
        await start_playback(chat_id)
    else:
        await call.leave_group_call(chat_id)

# ---------- Main ----------
async def main():
    # Start web server
    web_thread = Thread(target=run_web, daemon=True)
    web_thread.start()
    print(f"🌐 Web server started on port {PORT}")
    
    # Start clients
    print("Starting assistant...")
    await assistant.start()
    print("Starting bot...")
    await app.start()
    print("Starting voice calls...")
    await call.start()
    
    print("\n✅ **Music Bot is RUNNING!**")
    bot_info = await app.get_me()
    print(f"🤖 Bot: @{bot_info.username}")
    print(f"📡 Health check: http://localhost:{PORT}/health")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
