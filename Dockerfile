FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    ffmpeg gcc g++ python3-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Build cache ကိုချိုးဖျက်ရန်
RUN echo "Building on: $(date)"

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
