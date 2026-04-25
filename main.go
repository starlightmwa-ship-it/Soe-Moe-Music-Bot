// main.go
package main

import (
	"context"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/AshokShau/TgMusicBot/pkg/config"
	"github.com/AshokShau/TgMusicBot/pkg/core"
	"github.com/joho/godotenv"
)

func main() {
	// Load .env file
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using environment variables")
	}

	// ============ YOUR CONFIGURATION (ALREADY FILLED) ============
	cfg := &config.Config{
		APIID:        31427123,
		APIHash:      "27b540811ee6d2423f86a779848515ee",
		Token:        "8783739539:AAFPM95HIrSJQ-yoPtc-r8guZ-QJFgPymWA",
		String1:      "BQHfijMAhGoy0E7GCe5gQSmdBtM3BEFfPGBsf_pZYjcsxvWGMp3aRc0hxttuse9Os-twV9sagL85JEIerGlVe46r4-HIvPqDXx-h14BtHfwZHEIeDJV02iD5hUkaXsgNZBXbObhLPfE0t3QNIVlnGmG9eHhzjC_HxTW7KDhAJFLI1FQddmCYfsIGo5F-km0v6sig-XaYbL8q2RaDImfHBs2dfjrS8IvpETf2WnufIAwpTuhAb2aUYkwyLnTPYYgtqvD1Uro63tpssTzQA8WYn0c1E0Xf1JnVCVpoqUqYK2sSiCPRRGZXONpjENQ-Ogk1cdZlC1vSv3B5le3U17ccvEtuyjSsNwAAAAGmRHBgAA",
		OwnerID:      6904606472,
		LoggerID:     0, // Optional: Set your log group ID if needed
		SessionType:  "pyrogram",
		MongoURI:     os.Getenv("MONGO_URI"), // Optional: Can be empty for basic features
	}

	// Initialize and run bot
	bot := core.NewBot(cfg)
	ctx, cancel := context.WithCancel(context.Background())

	// Handle shutdown signals
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-sigChan
		log.Println("Shutting down...")
		cancel()
	}()

	log.Println("==================================================")
	log.Println("🎵 TgMusicBot (Go Version) STARTING...")
	log.Println("==================================================")

	if err := bot.Run(ctx); err != nil {
		log.Fatalf("Bot failed: %v", err)
	}
}
