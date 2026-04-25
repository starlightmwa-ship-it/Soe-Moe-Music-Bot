# plugins/play.py
import yt_dlp
from pyrogram.types import Message

ydl_opts = {'format': 'bestaudio/best', 'quiet': True}

async def search_youtube(query: str):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            track = info['entries'][0] if 'entries' in info else info
            return {
                'title': track.get('title', 'Unknown'),
                'url': track.get('webpage_url'),
                'duration': track.get('duration', 0),
            }
        except:
            return None

async def play(client, message: Message, bot, user, queues):
    query = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
    if not query:
        await message.reply("Usage: `/play <song name>`")
        return
    
    msg = await message.reply(f"🔍 Searching `{query[:50]}`...")
    track = await search_youtube(query)
    
    if not track:
        await msg.edit("❌ No results found!")
        return
    
    chat_id = message.chat.id
    
    if chat_id not in queues:
        queues[chat_id] = []
    
    if not queues[chat_id] and not await is_playing(user, chat_id):
        from pytgcalls import PyTgCalls
        call = PyTgCalls(user)
        await call.start()
        await call.join_group_call(chat_id, track['url'])
        await msg.edit(f"✅ Playing: **{track['title'][:50]}**")
    else:
        queues[chat_id].append(track)
        await msg.edit(f"➕ Added to queue: **{track['title'][:50]}**")

async def is_playing(user, chat_id):
    try:
        from pyrogram.enums import ChatMemberStatus
        member = await user.get_chat_member(chat_id, "me")
        return member.status == ChatMemberStatus.MEMBER
    except:
        return False
