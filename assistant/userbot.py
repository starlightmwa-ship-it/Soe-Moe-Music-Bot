# assistant/userbot.py
from pyrogram import Client
from config import API_ID, API_HASH, ASSISTANT_SESSION

# :memory: အစား assistant.session ဖိုင်ကို သုံးပါ
assistant = Client(
    "assistant",                     # session ဖိုင်အမည် (assistant.session)
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=ASSISTANT_SESSION
)
