import asyncio
import aiohttp

URL = "https://your-app.onrender.com"

async def auto_ping():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                await session.get(URL)
        except:
            pass
        await asyncio.sleep(600)
