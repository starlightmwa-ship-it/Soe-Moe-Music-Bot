FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    ffmpeg gcc g++ python3-dev libffi-dev libnacl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install cffi pycparser
RUN pip install pyrogram tgcrypto yt-dlp aiofiles python-dotenv
RUN pip install pycryptodome libtgvoip
RUN pip install pytgcalls --no-deps
RUN pip install pip --upgrade  # optional

COPY . .

CMD ["python", "main.py"]
