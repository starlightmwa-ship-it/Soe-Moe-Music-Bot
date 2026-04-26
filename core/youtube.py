import yt_dlp

def search(query):
    with yt_dlp.YoutubeDL({"format": "bestaudio"}) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]

    return {
        "title": info["title"],
        "url": info["url"],
        "thumb": info["thumbnail"]
    }
