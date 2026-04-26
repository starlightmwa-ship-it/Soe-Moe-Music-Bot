from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸", callback_data="pause"),
            InlineKeyboardButton("▶️", callback_data="resume"),
            InlineKeyboardButton("⏭", callback_data="skip")
        ],
        [
            InlineKeyboardButton("⏹", callback_data="stop")
        ]
    ])
