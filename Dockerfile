FROM python:3.10-slim

WORKDIR /app

# Install FFmpeg (required for audio streaming)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "main:web_app", "--bind", "0.0.0.0:8080", "--worker-class", "sync", "--timeout", "120"]
