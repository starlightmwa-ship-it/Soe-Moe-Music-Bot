from pyrogram import Client
from database.settings import set_lang, toggle_admin, get_settings
from core.lang import t
from plugins.settings import settings_buttons

@Client.on_callback_query()
async def settings_cb(client, cb):
    chat_id = cb.message.chat.id

    if cb.data == "lang_mm":
        await set_lang(chat_id, "mm")

    elif cb.data == "lang_en":
        await set_lang(chat_id, "en")

    elif cb.data == "admin_toggle":
        await toggle_admin(chat_id)

    data = await get_settings(chat_id)

    await cb.message.edit_text(
        t(data["lang"], "settings"),
        reply_markup=settings_buttons(data["lang"], data["admin_only"])
    )

    await cb.answer(t(data["lang"], "lang_set"))
