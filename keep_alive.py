# keep_alive.py
from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive on Render!"

@app.route('/health')
def health():
    return "OK", 200

def run():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    """Start a thread to keep the bot alive on Render"""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("✅ HTTP Server started for port binding")
