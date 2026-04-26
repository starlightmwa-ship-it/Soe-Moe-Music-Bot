from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from assistant.userbot import app

call = PyTgCalls(app)

async def start_call():
    await call.start()

async def join_and_play(chat_id, url):
    await call.join_group_call(chat_id, AudioPiped(url))

async def stop(chat_id):
    await call.leave_group_call(chat_id)
