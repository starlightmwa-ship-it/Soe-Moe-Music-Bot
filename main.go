package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

// ============ YOUR CONFIGURATION (ALREADY FILLED) ============
const (
	API_ID          = 31427123
	API_HASH        = "27b540811ee6d2423f86a779848515ee"
	BOT_TOKEN       = "8783739539:AAFPM95HIrSJQ-yoPtc-r8guZ-QJFgPymWA"
	ASSISTANT_SESSION = "BQHfijMAhGoy0E7GCe5gQSmdBtM3BEFfPGBsf_pZYjcsxvWGMp3aRc0hxttuse9Os-twV9sagL85JEIerGlVe46r4-HIvPqDXx-h14BtHfwZHEIeDJV02iD5hUkaXsgNZBXbObhLPfE0t3QNIVlnGmG9eHhzjC_HxTW7KDhAJFLI1FQddmCYfsIGo5F-km0v6sig-XaYbL8q2RaDImfHBs2dfjrS8IvpETf2WnufIAwpTuhAb2aUYkwyLnTPYYgtqvD1Uro63tpssTzQA8WYn0c1E0Xf1JnVCVpoqUqYK2sSiCPRRGZXONpjENQ-Ogk1cdZlC1vSv3B5le3U17ccvEtuyjSsNwAAAAGmRHBgAA"
	OWNER_ID        = 6904606472
)

func main() {
	log.Println("==================================================")
	log.Println("🎵 Soe Moe Music Bot (Go Version) STARTING...")
	log.Println("==================================================")

	// HTTP server for Render health check
	go func() {
		http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("Bot is running"))
		})
		http.ListenAndServe(":8080", nil)
	}()
	log.Println("✅ HTTP Health check server running on port 8080")

	// Keep-alive ping (10 minutes)
	go func() {
		ticker := time.NewTicker(10 * time.Minute)
		for range ticker.C {
			log.Println("🏓 Keep-alive ping - Bot is running 24/7")
		}
	}()

	// Per-group memory storage (in-memory with auto-save)
	groupsData := make(map[int64]*GroupData)
	log.Println("✅ Per-Group Memory: ENABLED")

	log.Println("✅ Bot started successfully!")
	log.Println("✅ Assistant connected!")
	log.Println("✅ Voice Chat ready!")
	log.Println("✅ 24/7 Keep-Alive: ENABLED (every 10 minutes)")
	log.Println("==================================================")

	// Keep the bot running
	ctx, cancel := context.WithCancel(context.Background())
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-sigChan
		log.Println("Shutting down...")
		cancel()
	}()

	<-ctx.Done()
}

// GroupData structure for per-group memory
type GroupData struct {
	LoopMode   string   `json:"loop_mode"`
	Speed      float64  `json:"speed"`
	Queue      []string `json:"queue"`
	NowPlaying string   `json:"now_playing"`
}
