import yt_dlp

def search(query):
    ydl_opts = {"format": "bestaudio", "quiet": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]

    return {
        "title": info["title"],
        "url": info["url"],
        "thumb": info["thumbnail"]
    }
