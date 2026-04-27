# plugins/__init__.py
from .play import play
from .pause import pause
from .resume import resume
from .skip import skip
from .stop import stop
from .queue import queue_cmd       # queue_cmd function ကို ထည့်သွင်းခြင်း
from .loop import loop
from .shuffle import shuffle
from .speed import speed
from .auth import auth, unauth
from .settings import setting
