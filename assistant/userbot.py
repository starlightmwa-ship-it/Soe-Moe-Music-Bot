# assistant/userbot.py
import os
from pyrogram import Client

# Environment Variables မှန်ကန်စွာ ဖတ်ပါ
API_ID = int(os.getenv("API_ID", 31427123))
API_HASH = os.getenv("API_HASH", "27b540811ee6d2423f86a779848515ee")
ASSISTANT_SESSION = os.getenv("ASSISTANT_SESSION", "BQHfijMAhGoy0E7GCe5gQSmdBtM3BEFfPGBsf_pZYjcsxvWGMp3aRc0hxttuse9Os-twV9sagL85JEIerGlVe46r4-HIvPqDXx-h14BtHfwZHEIeDJV02iD5hUkaXsgNZBXbObhLPfE0t3QNIVlnGmG9eHhzjC_HxTW7KDhAJFLI1FQddmCYfsIGo5F-km0v6sig-XaYbL8q2RaDImfHBs2dfjrS8IvpETf2WnufIAwpTuhAb2aUYkwyLnTPYYgtqvD1Uro63tpssTzQA8WYn0c1E0Xf1JnVCVpoqUqYK2sSiCPRRGZXONpjENQ-Ogk1cdZlC1vSv3B5le3U17ccvEtuyjSsNwAAAAGmRHBgAA")

# Create the Assistant Userbot client
app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=ASSISTANT_SESSION
)
