# plugins/play.py
import yt_dlp
import asyncio
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import AUTO_DELETE_SECONDS

ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
}

async def get_player_buttons(is_playing=True):
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

async def search_youtube(query):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if info['entries']:
                track = info['entries'][0]
                return {
                    'title': track['title'],
                    'url': track['webpage_url'],
                    'duration': track.get('duration', 0),
                    'thumbnail': track.get('thumbnail', ''),
                }
        except:
            return None

async def play(client, message: Message, bot, assistant, queues, group_settings):
    chat_id = message.chat.id
    query = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
    
    if not query:
        msg = await message.reply("⚠️ Usage: `/play <song name>`")
        await asyncio.sleep(AUTO_DELETE_SECONDS)
        await msg.delete()
        await message.delete()
        return
    
    status_msg = await message.reply(f"🔍 Searching `{query[:50]}`...")
    
    track = await search_youtube(query)
    if not track:
        await status_msg.edit("❌ No results found!")
        await asyncio.sleep(AUTO_DELETE_SECONDS)
        await status_msg.delete()
        await message.delete()
        return
    
    if chat_id not in queues:
        queues[chat_id] = []
    
    if not queues[chat_id] and not assistant.is_connected(chat_id):
        await status_msg.edit(f"✅ Playing: **{track['title'][:50]}**")
        
        # Send player panel with thumbnail
        player_msg = await bot.send_photo(
            chat_id,
            track['thumbnail'],
            caption=f"🎵 **Now Playing**\n[{track['title'][:50]}]({track['url']})",
            reply_markup=await get_player_buttons()
        )
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(track['url'], download=False)
            audio_url = info['url']
        
        await assistant.join_group_call(chat_id, audio_url)
        await status_msg.delete()
    else:
        queues[chat_id].append(track)
        await status_msg.edit(f"➕ Added to queue: **{track['title'][:50]}**\n📋 Position: `{len(queues[chat_id])}`")
        await asyncio.sleep(AUTO_DELETE_SECONDS)
        await status_msg.delete()
        await message.delete()
