FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pyrogram အတွက် speedup (optional)
RUN pip install tgcrypto

CMD ["gunicorn", "main:web_app", "--bind", "0.0.0.0:8080", "--worker-class", "sync", "--timeout", "120"]
