# assistant/userbot.py
from pyrogram import Client
from config import API_ID, API_HASH, ASSISTANT_SESSION

assistant = Client(
    "assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=ASSISTANT_SESSION
)
