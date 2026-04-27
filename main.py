# main.py
from pyrogram import Client
from pytgcalls import PyTgCalls
from config import API_ID, API_HASH, ASSISTANT_SESSION

# ဒီနေရာမှာ အောက်ပါအတိုင်း ဖြစ်ရပါမယ်
assistant = Client(":memory:", api_id=API_ID, api_hash=API_HASH, session_string=ASSISTANT_SESSION)
call = PyTgCalls(assistant)

async def start_services():
    await assistant.start()
    await call.start()
