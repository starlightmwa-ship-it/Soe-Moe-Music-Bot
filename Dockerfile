FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
# pytgcalls နောက်ဆုံး အလုပ်ဖြစ်တဲ့ ဗားရှင်းကို သီးသန့်ထည့်ပါ
RUN pip install "pytgcalls==3.0.0" --no-deps
# ဒီ command ကတော့ လိုအပ်တဲ့ dependencies အားလုံးကို မပျောက်အောင် ပြန်ထည့်ပေးပါတယ်
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
