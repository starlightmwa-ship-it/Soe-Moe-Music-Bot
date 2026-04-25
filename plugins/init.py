# plugins/__init__.py
from typing import Dict, List
from pyrogram import filters

# Global queue storage
queues: Dict[int, List[dict]] = {}
active_calls: Dict[int, bool] = {}

from .play import play
from .pause import pause
from .resume import resume
from .skip import skip
from .stop import stop
from .queue import queue_cmd
from .loop import loop
from .shuffle import shuffle
from .speed import speed
