# core/player.py (သို့) main.py
from pyrogram import Client
from pytgcalls import PyTgCalls
from config import API_ID, API_HASH, ASSISTANT_SESSION

# 1. Assistant Client ကို ဖန်တီးပါ
assistant = Client(
    ":memory:", # session string ကို တိုက်ရိုက်သုံးမယ်ဆိုရင် memory ကို သုံးပါ
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=ASSISTANT_SESSION
)

# 2. PyTgCalls ကို Assistant နဲ့ Initialize လုပ်ပါ
call = PyTgCalls(assistant)

async def start_call():
    await assistant.start()  # Assistant ကို အရင်စတင်ပါ
    await call.start()       # ပြီးမှ Call ကိုစတင်ပါ
