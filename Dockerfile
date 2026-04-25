FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg gcc g++ python3-dev libffi-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install cffi pycparser pyrogram tgcrypto yt-dlp aiofiles python-dotenv pycryptodome pytgcalls --no-deps

COPY . .

CMD ["python", "main.py"]
