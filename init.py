# database/__init__.py
import json
import aiofiles

async def load_data(filename):
    try:
        async with aiofiles.open(filename, 'r') as f:
            return json.loads(await f.read())
    except:
        return {}

async def save_data(filename, data):
    async with aiofiles.open(filename, 'w') as f:
        await f.write(json.dumps(data, indent=2))
