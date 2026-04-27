# assistant/userbot.py
from pyrogram import Client
from config import API_ID, API_HASH, ASSISTANT_SESSION

# Session ကို memory မှာမသိမ်းဘဲ file ထဲမှာ သိမ်းပါ
assistant = Client(
    "assistant",  # session file name (assistant.session)
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=ASSISTANT_SESSION
)
