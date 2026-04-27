# core/player.py (သို့) main.py
from pyrogram import Client
from pytgcalls import PyTgCalls
from config import API_ID, API_HASH, ASSISTANT_SESSION

# 1. Assistant Client ကို ဖန်တီးပါ
assistant = Client(":memory:", api_id=API_ID, api_hash=API_HASH, session_string=ASSISTANT_SESSION)
call = PyTgCalls(assistant)

async def start_call():
    await assistant.start()
    await call.start()
