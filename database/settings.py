from database.mongo import db

DEFAULT = {
    "lang": "en",
    "admin_only": False
}

async def get_settings(chat_id):
    data = await db.settings.find_one({"chat_id": chat_id})
    if not data:
        await db.settings.insert_one({"chat_id": chat_id, **DEFAULT})
        return DEFAULT
    return data

async def set_lang(chat_id, lang):
    await db.settings.update_one(
        {"chat_id": chat_id},
        {"$set": {"lang": lang}},
        upsert=True
    )

async def toggle_admin(chat_id):
    data = await get_settings(chat_id)
    new = not data.get("admin_only", False)

    await db.settings.update_one(
        {"chat_id": chat_id},
        {"$set": {"admin_only": new}},
        upsert=True
    )

    return new
