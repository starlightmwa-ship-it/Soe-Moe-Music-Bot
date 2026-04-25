# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
API_ID = int(os.environ.get("API_ID", 31427123))
API_HASH = os.environ.get("API_HASH", "27b540811ee6d2423f86a779848515ee")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8783739539:AAFPM95HIrSJQ-yoPtc-r8guZ-QJFgPymWA")
SESSION_STRING = os.environ.get("ASSISTANT_SESSION", "BQHfijMAhGoy0E7GCe5gQSmdBtM3BEFfPGBsf_pZYjcsxvWGMp3aRc0hxttuse9Os-twV9sagL85JEIerGlVe46r4-HIvPqDXx-h14BtHfwZHEIeDJV02iD5hUkaXsgNZBXbObhLPfE0t3QNIVlnGmG9eHhzjC_HxTW7KDhAJFLI1FQddmCYfsIGo5F-km0v6sig-XaYbL8q2RaDImfHBs2dfjrS8IvpETf2WnufIAwpTuhAb2aUYkwyLnTPYYgtqvD1Uro63tpssTzQA8WYn0c1E0Xf1JnVCVpoqUqYK2sSiCPRRGZXONpjENQ-Ogk1cdZlC1vSv3B5le3U17ccvEtuyjSsNwAAAAGmRHBgAA")
OWNER_ID = int(os.environ.get("OWNER_ID", 6904606472))

# Queue Settings
MAX_QUEUE_SIZE = 20

# Video/Audio Settings
STREAM_FORMAT = "bestaudio"  # only audio, no video
