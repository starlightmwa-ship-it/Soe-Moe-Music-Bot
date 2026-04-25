FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install pyrogram tgcrypto yt-dlp aiofiles python-dotenv pytgcalls pycryptodome

COPY . .

CMD ["python", "main.py"]
