FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install pytgcalls==3.0.0.dev24 --no-deps
RUN pip install yt-dlp --upgrade

COPY . .

CMD ["python", "main.py"]
