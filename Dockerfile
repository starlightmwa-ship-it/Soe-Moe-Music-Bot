FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Session file အတွက် write permission ပေးပါ
RUN chmod -R 777 /app

CMD ["python", "main.py"]
