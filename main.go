package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/AshokShau/TgMusicBot"
)

// ============ YOUR CONFIGURATION (သင့် ID များ ထည့်ပြီးသား) ============
const (
	API_ID           = 31427123
	API_HASH         = "27b540811ee6d2423f86a779848515ee"
	BOT_TOKEN        = "8783739539:AAFPM95HIrSJQ-yoPtc-r8guZ-QJFgPymWA"
	ASSISTANT_SESSION = "BQHfijMAhGoy0E7GCe5gQSmdBtM3BEFfPGBsf_pZYjcsxvWGMp3aRc0hxttuse9Os-twV9sagL85JEIerGlVe46r4-HIvPqDXx-h14BtHfwZHEIeDJV02iD5hUkaXsgNZBXbObhLPfE0t3QNIVlnGmG9eHhzjC_HxTW7KDhAJFLI1FQddmCYfsIGo5F-km0v6sig-XaYbL8q2RaDImfHBs2dfjrS8IvpETf2WnufIAwpTuhAb2aUYkwyLnTPYYgtqvD1Uro63tpssTzQA8WYn0c1E0Xf1JnVCVpoqUqYK2sSiCPRRGZXONpjENQ-Ogk1cdZlC1vSv3B5le3U17ccvEtuyjSsNwAAAAGmRHBgAA"
	OWNER_ID         = 6904606472
)

func main() {
	log.Println("==================================================")
	log.Println("🎵 Soe Moe Music Bot (Go + POLLING Mode) STARTING...")
	log.Println("==================================================")

	// ===== 1️⃣ HTTP Health Check Server (Render အတွက်) =====
	go func() {
		http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("Bot is running (Polling Mode)"))
		})
		log.Println("✅ Health check server started on :8080")
		http.ListenAndServe(":8080", nil)
	}()

	// ===== 2️⃣ Keep-Alive Ping (10 မိနစ်တစ်ခါ) =====
	go func() {
		ticker := time.NewTicker(10 * time.Minute)
		for range ticker.C {
			log.Println("🏓 Keep-alive ping - Bot is alive")
		}
	}()

	// ===== 3️⃣ Webhook ကို ရှင်းပြီး Polling Mode နဲ့ Bot စတင်ခြင်း =====
	// TgMusicBot instance ဖန်တီးခြင်း
	bot, err := TgMusicBot.NewBot(&TgMusicBot.Config{
		APIID:    API_ID,
		APIHash:  API_HASH,
		Token:    BOT_TOKEN,
		String1:  ASSISTANT_SESSION,
		OwnerID:  OWNER_ID,
		MongoURI: "", // MongoURI မရှိရင် ဗလာထားပါ
	})
	if err != nil {
		log.Fatalf("❌ Failed to create bot: %v", err)
	}

	// Webhook URL ကို အတင်းဖျက်မယ် (Force Delete)
	deleteWebhookURL := "https://api.telegram.org/bot" + BOT_TOKEN + "/deleteWebhook"
	resp, err := http.Get(deleteWebhookURL)
	if err == nil {
		log.Println("✅ Webhook deleted successfully:", resp.Status)
	} else {
		log.Println("⚠️ Webhook delete request failed:", err)
	}

	// Polling Mode စတင်ခြင်း
	log.Println("🔄 Starting bot in POLLING mode...")
	err = bot.StartPolling(context.Background())
	if err != nil {
		log.Fatalf("❌ Polling mode failed: %v", err)
	}

	// ===== 4️⃣ Graceful Shutdown (Server ပိတ်တဲ့အခါ သေချာရပ်စေရန်) =====
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	log.Println("🛑 Shutting down bot...")
	bot.Stop()
	log.Println("✅ Bot stopped gracefully")
}
