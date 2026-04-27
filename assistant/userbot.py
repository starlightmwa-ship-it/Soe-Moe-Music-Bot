# assistant/userbot.py
from pyrogram import Client
from config import API_ID, API_HASH, ASSISTANT_SESSION

async def init_assistant():
    # try:
    #     await assistant.start()
    #     return assistant
    # except Exception as e:
    #     print(f"Assistant start error: {e}")
    #     return None
    assistant = Client(
        "assistant",  # session name
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=ASSISTANT_SESSION
    )
    return assistant
