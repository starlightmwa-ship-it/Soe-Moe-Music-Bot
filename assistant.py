import yt_dlp
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped, InputStream

from config import API_ID, API_HASH, STRING_SESSION

user = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)
call = PyTgCalls(user)

def yt(query):
    ydl = yt_dlp.YoutubeDL({"format":"bestaudio","quiet":True})
    info = ydl.extract_info(f"ytsearch:{query}", download=False)
    d = info["entries"][0]
    return d["url"], d["title"], d["thumbnail"], d.get("duration", 0)

async def join(chat_id, url):
    await call.join_group_call(chat_id, InputStream(AudioPiped(url)))

async def change(chat_id, url):
    await call.change_stream(chat_id, InputStream(AudioPiped(url)))

async def leave(chat_id):
    await call.leave_group_call(chat_id)

async def start():
    await user.start()
    await call.start()
