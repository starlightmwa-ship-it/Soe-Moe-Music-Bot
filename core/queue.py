from collections import deque

queues = {}

def get_queue(chat_id):
    return queues.setdefault(chat_id, deque())

def add(chat_id, song):
    get_queue(chat_id).append(song)

def next_song(chat_id):
    q = get_queue(chat_id)
    return q[1] if len(q) > 1 else None

def pop(chat_id):
    if get_queue(chat_id):
        get_queue(chat_id).popleft()
