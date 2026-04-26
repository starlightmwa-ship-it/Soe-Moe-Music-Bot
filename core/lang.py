LANG = {
    "en": {
        "settings": "⚙ Settings",
        "admin_on": "👮 Admin Only: ON",
        "admin_off": "👮 Admin Only: OFF",
        "lang_set": "Language updated",
        "no_admin": "❌ Admin only command"
    },
    "mm": {
        "settings": "⚙ စနစ်များ",
        "admin_on": "👮 Admin Only: ဖွင့်ထားသည်",
        "admin_off": "👮 Admin Only: ပိတ်ထားသည်",
        "lang_set": "ဘာသာပြန်ပြောင်းပြီးပါပြီ",
        "no_admin": "❌ Admin မဟုတ်ပါ"
    }
}

def t(lang, key):
    return LANG.get(lang, LANG["en"]).get(key, key)
