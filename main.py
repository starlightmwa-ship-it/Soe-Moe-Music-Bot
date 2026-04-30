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

# PyTgCalls
from pytgcalls import GroupCallFactory
from pytgcalls.types.input_stream import AudioStream, InputStream
from pytgcalls.types.input_stream.audio import YouTubeAudio

# ---------- Config ----------
API_ID = int(os.environ.get("API_ID", 31427123))
API_HASH = os.environ.get("API_HASH", "27b540811ee6d2423f86a779848515ee")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8783739539:AAFPM95HIrSJQ-yoPtc-r8guZ-QJFgPymWA")
ASSISTANT_SESSION = os.environ.get("ASSISTANT_SESSION", "BQHfijMAhGoy0E7GCe5gQSmdBtM3BEFfPGBsf_pZYjcsxvWGMp3aRc0hxttuse9Os-twV9sagL85JEIerGlVe46r4-HIvPqDXx-h14BtHfwZHEIeDJV02iD5hUkaXsgNZBXbObhLPfE0t3QNIVlnGmG9eHhzjC_HxTW7KDhAJFLI1FQddmCYfsIGo5F-km0v6sig-XaYbL8q2RaDImfHBs2dfjrS8IvpETf2WnufIAwpTuhAb2aUYkwyLnTPYYgtqvD1Uro63tpssTzQA8WYn0c1E0Xf1JnVCVpoqUqYK2sSiCPRRGZXONpjENQ-Ogk1cdZlC1vSv3B5le3U17ccvEtuyjSsNwAAAAGmRHBgAA")
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://fighterlitboy_db_user:Soemoeaung@cluster0.es1n0kv.mongodb.net/?appName=Cluster0")
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

# Voice Call
group_call_factory = GroupCallFactory(assistant)
call = group_call_factory.get_group_call()

# ---------- Data ----------
queues: Dict[int, List[Dict]] = {}
now_playing: Dict[int, Dict] = {}

# ---------- Helper Functions ----------
async def get_audio_details(query: str, requester: str = ""):
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
            "thumbnail": info.get('thumbnail', ''),
            "requester": requester
        }

async def start_playback(chat_id: int):
    if chat_id not in queues or len(queues[chat_id]) == 0:
        return
    
    song = queues[chat_id].pop(0)
    now_playing[chat_id] = song
    
    try:
        await call.start(chat_id)
        await call.set_stream(chat_id, YouTubeAudio(song['url']))
        
        duration_min = song['duration'] // 60
        duration_sec = song['duration'] % 60
        text = f"**▶️ Now Playing**\n\n🎵 **{song['title'][:60]}**\n⏱ `{duration_min}:{duration_sec:02d}`\n👤 {song['requester']}"
        
        if song.get('thumbnail'):
            await app.send_photo(chat_id, song['thumbnail'], caption=text)
        else:
            await app.send_message(chat_id, text)
    except Exception as e:
        print(f"Playback error: {e}")

# ---------- BOT COMMANDS (Group + Private) ----------

# Start command
@app.on_message(filters.command("start"))
async def start_command(_, message: Message):
    text = """**🎵 Music Bot**

ကျွန်တော်က Voice Chat မှာ YouTube သီချင်းတွေ ဖွင့်ပေးတဲ့ Bot ပါ။

**Commands:**
/play [နာမည်/link] - သီချင်းဖွင့်မယ်
/pause - ခဏရပ်မယ်
/resume - ပြန်ဖွင့်မယ်
/skip - နောက်တစ်ပုဒ်သွားမယ်
/end - ဖွင့်တာရပ်မယ်
/queue - တန်းစီစာရင်း
/ping - Bot အသက်ရှိမရှိစစ်မယ်
/help - Command စာရင်း

**အသုံးပြုပုံ:** `/play မိုးည`"""
    await message.reply(text)

# Help command
@app.on_message(filters.command("help"))
async def help_command(_, message: Message):
    text = """**📖 Command List**

**Playback:**
/play [နာမည်/link] - Play music
/pause - Pause playback
/resume - Resume playback
/skip - Skip to next
/end - Stop playback

**Queue:**
/queue - Show queue list

**Others:**
/ping - Check bot status
/start - Show welcome message

**Examples:**
`/play မိုးည`
`/play https://youtube.com/watch?v=...`"""
    await message.reply(text)

# Play command (Group only)
@app.on_message(filters.command("play") & filters.group)
async def play_command(_, message: Message):
    chat_id = message.chat.id
    
    if len(message.command) < 2:
        await message.reply("❓ **အသုံးပြုပုံ:** `/play သီချင်းနာမည်`")
        return
    
    query = " ".join(message.command[1:])
    msg = await message.reply("🔍 **YouTube မှာ ရှာနေပါတယ်...**")
    
    song = await get_audio_details(query, message.from_user.first_name)
    
    if not song.get('url'):
        await msg.edit("❌ **သီချင်းမတွေ့ပါဘူး**")
        await asyncio.sleep(5)
        await msg.delete()
        return
    
    if chat_id not in queues:
        queues[chat_id] = []
    queues[chat_id].append(song)
    
    if chat_id not in now_playing:
        await msg.edit(f"▶️ **ဖွင့်နေပါတယ်:** {song['title'][:50]}")
        await start_playback(chat_id)
    else:
        await msg.edit(f"✅ **Queue ထဲထည့်လိုက်ပါပြီ**\n🎵 {song['title'][:50]}\n📍 Position: {len(queues[chat_id])}")
        await asyncio.sleep(10)
        await msg.delete()

# Pause command
@app.on_message(filters.command("pause") & filters.group)
async def pause_command(_, message: Message):
    try:
        await call.pause_stream(message.chat.id)
        await message.reply("⏸ **Paused**")
    except Exception as e:
        await message.reply(f"❌ {str(e)[:100]}")

# Resume command
@app.on_message(filters.command("resume") & filters.group)
async def resume_command(_, message: Message):
    try:
        await call.resume_stream(message.chat.id)
        await message.reply("▶️ **Resumed**")
    except Exception as e:
        await message.reply(f"❌ {str(e)[:100]}")

# Skip command
@app.on_message(filters.command("skip") & filters.group)
async def skip_command(_, message: Message):
    chat_id = message.chat.id
    try:
        await call.stop(chat_id)
        now_playing.pop(chat_id, None)
        if chat_id in queues and len(queues[chat_id]) > 0:
            await start_playback(chat_id)
            await message.reply("⏭ **Skipped**")
        else:
            await message.reply("⏹ **Queue ကုန်ပါပြီ**")
    except Exception as e:
        await message.reply(f"❌ {str(e)[:100]}")

# End command
@app.on_message(filters.command("end") & filters.group)
async def end_command(_, message: Message):
    chat_id = message.chat.id
    try:
        await call.stop(chat_id)
        queues[chat_id] = []
        now_playing.pop(chat_id, None)
        await message.reply("🛑 **Stopped**")
    except Exception as e:
        await message.reply(f"❌ {str(e)[:100]}")

# Queue command
@app.on_message(filters.command("queue") & filters.group)
async def queue_command(_, message: Message):
    chat_id = message.chat.id
    if chat_id not in queues or len(queues[chat_id]) == 0:
        await message.reply("📋 **Queue ထဲမှာ သီချင်းမရှိပါဘူး**")
    else:
        text = "**📋 Queue List**\n\n"
        for i, song in enumerate(queues[chat_id][:10], 1):
            text += f"{i}. {song['title'][:40]}\n"
        if len(queues[chat_id]) > 10:
            text += f"\n...နဲ့ {len(queues[chat_id]) - 10} ပုဒ်ထပ်ရှိသေးတယ်"
        await message.reply(text)

# Ping command
@app.on_message(filters.command("ping"))
async def ping_command(_, message: Message):
    start = datetime.now()
    msg = await message.reply("🏓 **Pong!**")
    end = datetime.now()
    latency = (end - start).microseconds / 1000
    await msg.edit(f"🏓 **Pong!**\n⏱ Latency: `{latency:.0f} ms`")

# Voice chat events
@call.on_stream_end()
async def on_stream_end(chat_id: int):
    now_playing.pop(chat_id, None)
    if chat_id in queues and len(queues[chat_id]) > 0:
        await start_playback(chat_id)
    else:
        await call.stop(chat_id)

# ---------- Main ----------
async def main():
    # Start web server
    web_thread = Thread(target=run_web, daemon=True)
    web_thread.start()
    print(f"🌐 Web server on port {PORT}")
    
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
    print(f"📡 Health: https://soe-moe-music-bot.onrender.com/health")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
