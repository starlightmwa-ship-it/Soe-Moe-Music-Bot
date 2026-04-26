# core/player.py
from pyrogram import Client
from pytgcalls import PyTgCalls
from config import API_ID, API_HASH, ASSISTANT_SESSION

# Assistant Client ကို ဦးစွာ Create လုပ်ပါ
assistant = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=ASSISTANT_SESSION
)

# PyTgCalls ကို assistant နဲ့ Initialize လုပ်ပါ
call = PyTgCalls(assistant)

async def start_call():
    await assistant.start()
    await call.start()
    print("✅ Assistant and voice call started!")

async def stop_call():
    await call.stop()
    await assistant.stop()
