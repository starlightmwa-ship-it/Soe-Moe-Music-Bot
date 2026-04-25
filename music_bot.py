# music_bot.py
# Music Bot with Per-Group Memory + 24/7 Keep Alive

import os
import asyncio
import json
import random
import yt_dlp
from datetime import datetime
from typing import Dict, List, Optional
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from pyrogram.enums import ChatMemberStatus
from functools import wraps
import aiofiles

# =================== CONFIGURATION ===================
API_ID = int(os.environ.get("API_ID", 31427123))
API_HASH = os.environ.get("API_HASH", "27b540811ee6d2423f86a779848515ee")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8783739539:AAFPM95HIrSJQ-yoPtc-r8guZ-QJFgPymWA")
ASSISTANT_SESSION = os.environ.get("ASSISTANT_SESSION", "EqjNDUzaEfECHJAkGV3IRxaeudjGHmTGYLNGUtBLWrFzx5hSzBXdGSP4afvkgj9G8gBvjVtN-GxRDftKR3Pes6XECYjV7iQ8EhCEFWYVo_fm_vO-S2GQ7Ih-R8KKlv7OpJv6zGd6Y8n3UjhQ1T6RNSrFk0vQBgfISrQAAAAGmRHBgAA")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))

MAX_QUEUE_SIZE = 20
GROUPS_FILE = "groups_data.json"

# Per-group memory storage
groups_data: Dict[int, dict] = {}
active_players: Dict[int, 'MusicPlayer'] = {}

# =================== EMOJIS ===================
E = {
    "play": "▶️", "pause": "⏸️", "stop": "⛔", "skip": "⏭️", "previous": "⏮️",
    "loop": "🔄", "queue": "📋", "player": "🎛️", "settings": "⚙️", "volume": "🔊",
    "speed": "⚡", "shuffle": "🎲", "search": "🔍", "add": "➕", "clear": "🗑️",
    "close": "❌", "success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️",
    "music_note": "🎵", "headphone": "🎧", "microphone": "🎤", "cd": "💿",
    "timer": "⏱️", "admin": "👑", "sparkles": "✨", "check": "✔️", "limit": "🚫"
}

# =================== DATA MANAGEMENT ===================
async def load_data():
    global groups_data
    try:
        async with aiofiles.open(GROUPS_FILE, "r") as f:
            groups_data = json.loads(await f.read())
    except:
        groups_data = {}

async def save_groups():
    async with aiofiles.open(GROUPS_FILE, "w") as f:
        await f.write(json.dumps(groups_data, indent=2))

async def get_group_setting(group_id: int, key: str, default):
    return groups_data.get(str(group_id), {}).get(key, default)

async def set_group_setting(group_id: int, key: str, value):
    if str(group_id) not in groups_data:
        groups_data[str(group_id)] = {}
    groups_data[str(group_id)][key] = value
    await save_groups()

def format_duration(seconds: int) -> str:
    if not seconds:
        return "Live"
    minutes = seconds // 60
    seconds = seconds % 60
    hours = minutes // 60
    if hours > 0:
        return f"{hours:02d}:{minutes % 60:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"

def get_progress_bar(percentage: int) -> str:
    filled = int(percentage / 5)
    empty = 20 - filled
    return "🟢" * filled + "⚪" * empty

# =================== MUSIC PLAYER CLASS ===================
class MusicPlayer:
    def __init__(self, group_id: int):
        self.group_id = group_id
        self.queue: List[dict] = []
        self.queue_history: List[dict] = []
        self.current: Optional[dict] = None
        self.is_playing = False
        self.is_paused = False
        self.loop_mode = "off"
        self.speed = 1.0
        self.volume = 50
        self.start_time = 0
        self.duration = 0
        self.message_id: Optional[int] = None
        self.thumbnail_msg_id: Optional[int] = None

    def add_to_queue(self, track: dict) -> tuple:
        if len(self.queue) >= MAX_QUEUE_SIZE:
            return False, 0, f"{E['limit']} Queue limit reached! Maximum {MAX_QUEUE_SIZE} tracks."
        self.queue.append(track)
        return True, len(self.queue), f"{E['add']} Added: **{track['title'][:40]}**\n{E['queue']} Position: `{len(self.queue)}`"

    async def update_player_panel(self, bot: Client):
        if not self.current:
            return
        
        current_time = int(asyncio.get_event_loop().time() - self.start_time) if self.start_time else 0
        duration = self.current.get('duration', 0)
        progress = int((current_time / duration) * 100) if duration > 0 else 0
        
        queue_count = len(self.queue)
        queue_info = f"{E['queue']} **Queue:** `{queue_count}/{MAX_QUEUE_SIZE}`"
        if queue_count >= MAX_QUEUE_SIZE:
            queue_info += f" {E['limit']}"
        
        caption = f"""
{E['music_note']} **NOW PLAYING** {E['headphone']}

**{self.current['title'][:50]}**
{E['microphone']} **Artist:** `{self.current['artist'][:30]}`
{E['timer']} **Duration:** `{format_duration(duration)}`

{get_progress_bar(progress)} `{format_duration(current_time)} / {format_duration(duration)}`

{E['speed']} **Speed:** `{self.speed}x` | {E['volume']} **Vol:** `{self.volume}%`
{E['loop']} **Loop:** `{self.loop_mode.upper()}` | {queue_info}
"""
        
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{E['pause']} Pause" if not self.is_paused else f"{E['play']} Resume", callback_data="pause_resume"),
             InlineKeyboardButton(f"{E['stop']} Stop", callback_data="stop"),
             InlineKeyboardButton(f"{E['skip']} Skip", callback_data="skip")],
            [InlineKeyboardButton(f"{E['previous']} Prev", callback_data="previous"),
             InlineKeyboardButton(f"{E['loop']} Loop", callback_data="loop"),
             InlineKeyboardButton(f"{E['shuffle']} Shuffle", callback_data="shuffle_queue")],
            [InlineKeyboardButton(f"{E['speed']} Speed", callback_data="speed_menu"),
             InlineKeyboardButton(f"{E['volume']} Vol", callback_data="volume_menu"),
             InlineKeyboardButton(f"{E['queue']} Queue", callback_data="show_queue")],
            [InlineKeyboardButton(f"{E['settings']} Settings", callback_data="settings"),
             InlineKeyboardButton(f"{E['close']} Close", callback_data="close_player")]
        ])
        
        if self.message_id:
            try:
                await bot.edit_message_caption(self.group_id, self.message_id, caption=caption, reply_markup=reply_markup)
            except:
                msg = await bot.send_message(self.group_id, caption, reply_markup=reply_markup)
                self.message_id = msg.id
        else:
            msg = await bot.send_message(self.group_id, caption, reply_markup=reply_markup)
            self.message_id = msg.id
        
        if self.current.get('thumbnail') and not self.thumbnail_msg_id:
            try:
                thumb_msg = await bot.send_photo(self.group_id, self.current['thumbnail'], caption=f"{E['music_note']} **{self.current['title'][:40]}**")
                self.thumbnail_msg_id = thumb_msg.id
            except:
                pass

    async def play_track(self, assistant: Client, bot: Client, track: dict):
        self.current = track
        self.is_playing = True
        self.is_paused = False
        self.start_time = asyncio.get_event_loop().time()
        self.duration = track.get('duration', 0)
        self.thumbnail_msg_id = None
        
        ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(track['url'], download=False)
            audio_url = info['url']
        
        await assistant.play_stream(self.group_id, audio_url, self.speed)
        await self.update_player_panel(bot)

    async def next_track(self, assistant: Client, bot: Client):
        if self.loop_mode == "one" and self.current:
            await self.play_track(assistant, bot, self.current)
        elif self.loop_mode == "all" and self.queue:
            recycled = self.queue.pop(0)
            self.queue.append(recycled)
            await self.play_track(assistant, bot, recycled)
        elif self.queue:
            next_track = self.queue.pop(0)
            if self.current:
                self.queue_history.append(self.current)
            await self.play_track(assistant, bot, next_track)
        else:
            self.is_playing = False
            self.current = None
            if self.message_id:
                try:
                    await bot.delete_messages(self.group_id, [self.message_id, self.thumbnail_msg_id])
                except:
                    pass
                self.message_id = None
                self.thumbnail_msg_id = None
            await bot.send_message(self.group_id, f"{E['check']} Queue finished!")

    async def previous_track(self, assistant: Client, bot: Client):
        if self.queue_history:
            prev = self.queue_history.pop()
            if self.current:
                self.queue.insert(0, self.current)
            await self.play_track(assistant, bot, prev)
        else:
            await bot.send_message(self.group_id, f"{E['warning']} No previous track!")

    async def shuffle_queue(self):
        if len(self.queue) > 1:
            random.shuffle(self.queue)
            return True
        return False

    def set_speed(self, speed: float):
        self.speed = max(0.5, min(2.0, speed))

    def toggle_loop(self):
        modes = ["off", "one", "all"]
        current_idx = modes.index(self.loop_mode)
        self.loop_mode = modes[(current_idx + 1) % 3]
        return self.loop_mode

# =================== DECORATORS ===================
def auto_delete(seconds: int = 8):
    def decorator(func):
        @wraps(func)
        async def wrapper(client, message):
            result = await func(client, message)
            if result and hasattr(result, 'delete'):
                await asyncio.sleep(seconds)
                try:
                    await result.delete()
                    await message.delete()
                except:
                    pass
            return result
        return wrapper
    return decorator

# =================== BOT INIT ===================
bot = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=ASSISTANT_SESSION)

async def search_youtube(query: str) -> Optional[dict]:
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'no_warnings': True, 'default_search': 'ytsearch1'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            track = info['entries'][0] if 'entries' in info else info
            return {
                'title': track.get('title', 'Unknown'),
                'artist': track.get('uploader', 'Unknown'),
                'url': track.get('webpage_url', track.get('original_url')),
                'duration': track.get('duration', 0),
                'thumbnail': track.get('thumbnail', ''),
            }
        except:
            return None

# =================== 24/7 KEEP ALIVE (Ping every 10 min) ===================
async def keep_alive():
    """Send ping to self every 10 minutes to keep bot awake"""
    while True:
        await asyncio.sleep(600)  # 10 minutes
        try:
            # Send ping to check if bot is alive
            print(f"[{datetime.now()}] 🏓 Keep Alive Ping - Bot is running")
            # Optionally try to send message to owner if needed
            if OWNER_ID:
                await bot.send_message(OWNER_ID, f"{E['check']} Bot is still alive! {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"Keep alive error: {e}")

# =================== COMMANDS ===================
@bot.on_message(filters.command(["start", "help"]))
@auto_delete(15)
async def start_cmd(client: Client, message: Message):
    text = f"""
{E['sparkles']} **MUSIC BOT v5.0** {E['headphone']}

{E['music_note']} High quality audio streaming
{E['cd']} Queue, Loop, Speed control
{E['shuffle']} Shuffle & Previous track
{E['limit']} Max queue: **{MAX_QUEUE_SIZE} tracks**

**📋 Commands:**
`/play` `<song>` - Play music
`/pause` - Pause playback
`/resume` - Resume playback
`/skip` - Skip current track
`/previous` - Play previous track
`/end` or `/stop` - Stop playback
`/queue` - Show queue
`/loop` - Toggle loop mode
`/shuffle` - Shuffle queue
`/speed` `<0.5-2.0>` - Change speed
`/setting` - Bot settings
"""
    return await message.reply(text)

@bot.on_message(filters.command("play") & filters.group)
@auto_delete(5)
async def play_cmd(client: Client, message: Message):
    query = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
    if not query:
        return await message.reply(f"{E['warning']} Usage: `/play song name`")
    
    status_msg = await message.reply(f"{E['search']} Searching `{query[:50]}`...")
    track = await search_youtube(query)
    
    if not track:
        await status_msg.edit(f"{E['error']} No results found!")
        return None
    
    group_id = message.chat.id
    if group_id not in active_players:
        active_players[group_id] = MusicPlayer(group_id)
    
    player = active_players[group_id]
    
    if not player.is_playing:
        await player.play_track(assistant, bot, track)
        await status_msg.edit(f"{E['success']} Playing: **{track['title'][:50]}**")
    else:
        success, position, msg_text = player.add_to_queue(track)
        await status_msg.edit(msg_text)
    
    return None

@bot.on_message(filters.command(["pause", "resume"]))
@auto_delete(5)
async def pause_resume_cmd(client: Client, message: Message):
    group_id = message.chat.id
    player = active_players.get(group_id)
    
    if not player or not player.is_playing:
        return await message.reply(f"{E['warning']} Nothing playing!")
    
    if message.command[0] == "pause" and not player.is_paused:
        await assistant.pause_stream(group_id)
        player.is_paused = True
        await player.update_player_panel(bot)
        await message.reply(f"{E['pause']} Paused")
    elif message.command[0] == "resume" and player.is_paused:
        await assistant.resume_stream(group_id)
        player.is_paused = False
        await player.update_player_panel(bot)
        await message.reply(f"{E['play']} Resumed")
    return None

@bot.on_message(filters.command("skip"))
@auto_delete(5)
async def skip_cmd(client: Client, message: Message):
    group_id = message.chat.id
    player = active_players.get(group_id)
    
    if not player or not player.is_playing:
        return await message.reply(f"{E['warning']} Nothing playing!")
    
    await assistant.stop_stream(group_id)
    await player.next_track(assistant, bot)
    await message.reply(f"{E['skip']} Skipped")
    return None

@bot.on_message(filters.command("previous"))
@auto_delete(5)
async def previous_cmd(client: Client, message: Message):
    group_id = message.chat.id
    player = active_players.get(group_id)
    
    if not player or not player.is_playing:
        return await message.reply(f"{E['warning']} Nothing playing!")
    
    await assistant.stop_stream(group_id)
    await player.previous_track(assistant, bot)
    await message.reply(f"{E['previous']} Playing previous track")
    return None

@bot.on_message(filters.command(["end", "stop"]))
@auto_delete(5)
async def stop_cmd(client: Client, message: Message):
    group_id = message.chat.id
    player = active_players.get(group_id)
    
    if player and player.is_playing:
        await assistant.stop_stream(group_id)
        player.is_playing = False
        player.current = None
        player.queue.clear()
        player.queue_history.clear()
        
        if player.message_id:
            try:
                await bot.delete_messages(group_id, [player.message_id, player.thumbnail_msg_id])
            except:
                pass
        player.message_id = None
        player.thumbnail_msg_id = None
        
        await message.reply(f"{E['stop']} Stopped playback")
    return None

@bot.on_message(filters.command("queue"))
@auto_delete(15)
async def queue_cmd(client: Client, message: Message):
    group_id = message.chat.id
    player = active_players.get(group_id)
    
    if not player or (not player.is_playing and not player.queue):
        return await message.reply(f"{E['warning']} Queue is empty!")
    
    text = f"{E['queue']} **MUSIC QUEUE** {E['queue']}\n\n"
    if player.current:
        text += f"{E['play']} **Now Playing:**\n`{player.current['title'][:50]}`\n\n"
    text += f"{E['info']} **Limit:** `{len(player.queue)}/{MAX_QUEUE_SIZE}` tracks\n\n"
    
    if player.queue:
        text += f"{E['cd']} **Up Next:**\n"
        for i, track in enumerate(player.queue[:15], 1):
            dur = format_duration(track.get('duration', 0))
            text += f"`{i}. {track['title'][:45]}` `[{dur}]`\n"
        if len(player.queue) > 15:
            text += f"\n... and {len(player.queue) - 15} more"
    else:
        text += f"{E['info']} No tracks in queue\n\n{E['add']} Add songs with `/play`"
    
    return await message.reply(text)

@bot.on_message(filters.command("loop"))
@auto_delete(5)
async def loop_cmd(client: Client, message: Message):
    group_id = message.chat.id
    player = active_players.get(group_id)
    
    if not player or not player.is_playing:
        return await message.reply(f"{E['warning']} Nothing playing!")
    
    new_mode = player.toggle_loop()
    await player.update_player_panel(bot)
    mode_text = {"off": "Disabled", "one": "🔂 Current Track", "all": "🔁 Entire Queue"}
    await message.reply(f"{E['loop']} Loop: **{mode_text[new_mode]}**")
    return None

@bot.on_message(filters.command("shuffle"))
@auto_delete(5)
async def shuffle_cmd(client: Client, message: Message):
    group_id = message.chat.id
    player = active_players.get(group_id)
    
    if not player or len(player.queue) < 2:
        return await message.reply(f"{E['warning']} Need at least 2 songs in queue!")
    
    if await player.shuffle_queue():
        await player.update_player_panel(bot)
        await message.reply(f"{E['shuffle']} Queue shuffled! ({len(player.queue)} tracks)")
    else:
        await message.reply(f"{E['error']} Failed to shuffle")
    return None

@bot.on_message(filters.command("speed"))
@auto_delete(5)
async def speed_cmd(client: Client, message: Message):
    args = message.text.split()
    if len(args) != 2:
        return await message.reply(f"{E['warning']} Usage: `/speed 0.5` to `/speed 2.0`")
    
    try:
        speed = float(args[1])
        if speed < 0.5 or speed > 2.0:
            raise ValueError
    except:
        return await message.reply(f"{E['error']} Invalid speed! Use 0.5 to 2.0")
    
    group_id = message.chat.id
    player = active_players.get(group_id)
    
    if not player or not player.is_playing:
        return await message.reply(f"{E['warning']} Nothing playing!")
    
    old_speed = player.speed
    player.set_speed(speed)
    current_track = player.current
    await assistant.stop_stream(group_id)
    await player.play_track(assistant, bot, current_track)
    await message.reply(f"{E['speed']} Speed: `{old_speed}x` → `{player.speed}x`")
    return None

@bot.on_message(filters.command("setting"))
@auto_delete(30)
async def settings_cmd(client: Client, message: Message):
    admin_setting = await get_group_setting(message.chat.id, "admin_only", False)
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{E['admin']} Admin Only: {'✅ ON' if admin_setting else '❌ OFF'}", callback_data="toggle_admin")],
        [InlineKeyboardButton(f"{E['close']} Close", callback_data="close_settings")]
    ])
    return await message.reply(f"{E['settings']} **Settings Panel**\n\nPer-group settings are saved automatically!", reply_markup=keyboard)

# =================== CALLBACK HANDLERS ===================
@bot.on_callback_query()
async def callback_handler(client: Client, callback: CallbackQuery):
    data = callback.data
    group_id = callback.message.chat.id
    player = active_players.get(group_id)
    
    try:
        if data == "pause_resume":
            if player and player.is_playing:
                if player.is_paused:
                    await assistant.resume_stream(group_id)
                    player.is_paused = False
                    await callback.answer("Resumed")
                else:
                    await assistant.pause_stream(group_id)
                    player.is_paused = True
                    await callback.answer("Paused")
                await player.update_player_panel(bot)
        
        elif data == "stop":
            if player and player.is_playing:
                await assistant.stop_stream(group_id)
                player.is_playing = False
                player.current = None
                player.queue.clear()
                player.queue_history.clear()
                if player.message_id:
                    try:
                        await bot.delete_messages(group_id, [player.message_id, player.thumbnail_msg_id])
                    except:
                        pass
                    player.message_id = None
                    player.thumbnail_msg_id = None
                await callback.message.delete()
                await callback.answer("Stopped")
        
        elif data == "skip":
            if player and player.is_playing:
                await assistant.stop_stream(group_id)
                await player.next_track(assistant, bot)
                await callback.answer("Skipped")
        
        elif data == "previous":
            if player and player.is_playing:
                await assistant.stop_stream(group_id)
                await player.previous_track(assistant, bot)
                await callback.answer("Previous")
        
        elif data == "loop":
            if player and player.is_playing:
                new_mode = player.toggle_loop()
                await player.update_player_panel(bot)
                await callback.answer(f"Loop: {new_mode}")
        
        elif data == "shuffle_queue":
            if player and player.is_playing and len(player.queue) >= 2:
                await player.shuffle_queue()
                await player.update_player_panel(bot)
                await callback.answer("Queue shuffled!")
            else:
                await callback.answer("Need 2+ songs!", show_alert=True)
        
        elif data == "show_queue":
            if not player or (not player.is_playing and not player.queue):
                await callback.answer("Queue empty!", show_alert=True)
            else:
                text = f"{E['queue']} **QUEUE** `({len(player.queue)}/{MAX_QUEUE_SIZE})`\n\n"
                if player.current:
                    text += f"**Now:** `{player.current['title'][:50]}`\n\n"
                if player.queue:
                    for i, t in enumerate(player.queue[:10], 1):
                        text += f"`{i}. {t['title'][:45]}`\n"
                await callback.message.reply(text, quote=False)
                await callback.answer()
        
        elif data == "speed_menu":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🐢 0.5x", callback_data="set_speed_0.5"), InlineKeyboardButton("1.0x", callback_data="set_speed_1.0"), InlineKeyboardButton("🐇 2.0x", callback_data="set_speed_2.0")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_player")]
            ])
            await callback.message.edit_reply_markup(reply_markup=keyboard)
            await callback.answer()
        
        elif data.startswith("set_speed_"):
            speed = float(data.split("_")[2])
            if player and player.is_playing:
                player.set_speed(speed)
                current_track = player.current
                await assistant.stop_stream(group_id)
                await player.play_track(assistant, bot, current_track)
                await callback.answer(f"Speed: {speed}x")
        
        elif data == "volume_menu":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔇 0%", callback_data="set_vol_0"), InlineKeyboardButton("🔉 50%", callback_data="set_vol_50"), InlineKeyboardButton("🔊 100%", callback_data="set_vol_100")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_player")]
            ])
            await callback.message.edit_reply_markup(reply_markup=keyboard)
            await callback.answer()
        
        elif data.startswith("set_vol_"):
            vol = int(data.split("_")[2])
            if player:
                player.volume = vol
                await callback.answer(f"Volume: {vol}%")
        
        elif data == "back_to_player":
            if player:
                await player.update_player_panel(bot)
            else:
                await callback.message.delete()
            await callback.answer()
        
        elif data == "settings":
            admin_setting = await get_group_setting(group_id, "admin_only", False)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{E['admin']} Admin Only: {'✅ ON' if admin_setting else '❌ OFF'}", callback_data="toggle_admin")],
                [InlineKeyboardButton(f"{E['close']} Close", callback_data="close_settings")]
            ])
            await callback.message.edit_reply_markup(reply_markup=keyboard)
            await callback.answer()
        
        elif data == "toggle_admin":
            current = await get_group_setting(group_id, "admin_only", False)
            await set_group_setting(group_id, "admin_only", not current)
            await callback.answer(f"Admin Only: {'ON' if not current else 'OFF'}")
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{E['admin']} Admin Only: {'✅ ON' if not current else '❌ OFF'}", callback_data="toggle_admin")],
                [InlineKeyboardButton(f"{E['close']} Close", callback_data="close_settings")]
            ])
            await callback.message.edit_reply_markup(reply_markup=keyboard)
        
        elif data in ["close_player", "close_settings"]:
            await callback.message.delete()
            await callback.answer()
    
    except Exception as e:
        await callback.answer(f"Error: {str(e)[:40]}", show_alert=True)

# =================== MAIN ===================
async def main():
    print("=" * 50)
    print("🎵 MUSIC BOT STARTING...")
    print("=" * 50)
    print(f"Max Queue Size: {MAX_QUEUE_SIZE} tracks")
    print(f"24/7 Keep Alive: Every 10 minutes")
    print(f"Per-Group Memory: ENABLED")
    print("=" * 50)
    
    await load_data()
    await bot.start()
    await assistant.start()
    
    print(f"\n✅ Bot started successfully!")
    print(f"✅ Assistant connected!")
    print(f"✅ Bot is now running 24/7")
    print("=" * 50)
    
    # Start keep alive task
    asyncio.create_task(keep_alive())
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
