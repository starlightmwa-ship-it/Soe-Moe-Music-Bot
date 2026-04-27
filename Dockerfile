FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# pip ကို အဆင့်မြှင့်ပါ
RUN pip install --upgrade pip

# pytgcalls ရဲ့ အလုပ်အဖြစ်ဆုံး ဗားရှင်းကို သီးသန့်တပ်ဆင်ပါ
RUN pip install "pytgcalls>=3.0.0.dev24" --no-deps

# လိုအပ်တဲ့ core dependencies တွေကို ပြန်တပ်ဆင်ပါ
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
