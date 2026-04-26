from database.mongo import db

async def get_settings(chat_id):
    data = await db.settings.find_one({"chat_id": chat_id})
    return data or {"lang": "en", "admin_only": False}

async def update_setting(chat_id, key, value):
    await db.settings.update_one(
        {"chat_id": chat_id},
        {"$set": {key: value}},
        upsert=True
    )
