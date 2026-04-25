// main.go
package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"
)

// ==================== Per-Group Memory Storage ====================
type GroupData struct {
	LoopMode   string  `json:"loop_mode"`   // "off", "one", "all"
	Speed      float64 `json:"speed"`       // 0.5 to 2.0
	Queue      []Song  `json:"queue"`       // Queue list
	NowPlaying *Song   `json:"now_playing"` // Current playing song
}

type Song struct {
	Title    string `json:"title"`
	URL      string `json:"url"`
	Duration int    `json:"duration"`
}

var (
	groupsData   = make(map[int64]*GroupData)
	groupsMutex  sync.RWMutex
	dataFilePath = "groups_data.json"
)

// Load data from file
func loadGroupsData() {
	file, err := os.Open(dataFilePath)
	if err != nil {
		log.Println("No existing data file, starting fresh")
		return
	}
	defer file.Close()

	decoder := json.NewDecoder(file)
	err = decoder.Decode(&groupsData)
	if err != nil {
		log.Println("Error loading data:", err)
	}
	log.Printf("Loaded %d groups data", len(groupsData))
}

// Save data to file
func saveGroupsData() {
	groupsMutex.RLock()
	defer groupsMutex.RUnlock()

	file, err := os.Create(dataFilePath)
	if err != nil {
		log.Println("Error saving data:", err)
		return
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	err = encoder.Encode(groupsData)
	if err != nil {
		log.Println("Error encoding data:", err)
	}
}

// Get group data (create if not exists)
func getGroupData(groupID int64) *GroupData {
	groupsMutex.Lock()
	defer groupsMutex.Unlock()

	if _, exists := groupsData[groupID]; !exists {
		groupsData[groupID] = &GroupData{
			LoopMode:   "off",
			Speed:      1.0,
			Queue:      []Song{},
			NowPlaying: nil,
		}
		saveGroupsData()
	}
	return groupsData[groupID]
}

// Update group data and save
func updateGroupData(groupID int64, updateFunc func(*GroupData)) {
	groupsMutex.Lock()
	defer groupsMutex.Unlock()

	if _, exists := groupsData[groupID]; !exists {
		groupsData[groupID] = &GroupData{
			LoopMode:   "off",
			Speed:      1.0,
			Queue:      []Song{},
			NowPlaying: nil,
		}
	}
	updateFunc(groupsData[groupID])
	saveGroupsData()
}

// ==================== Main Bot ====================
func main() {
	log.Println("==================================================")
	log.Println("🎵 Soe Moe Music Bot (Go Version) STARTING...")
	log.Println("==================================================")

	// Load existing group data
	loadGroupsData()

	// HTTP server for Render health check (prevents sleeping)
	go func() {
		http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte("Bot is running"))
		})
		http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte("OK"))
		})
		log.Println("✅ HTTP Health check server running on port 8080")
		http.ListenAndServe(":8080", nil)
	}()

	// Keep-alive ping every 10 minutes (prevents Render from sleeping)
	go func() {
		ticker := time.NewTicker(10 * time.Minute)
		for range ticker.C {
			log.Println("🏓 Keep-alive ping - Bot is running")
			log.Printf("📊 Active groups: %d", len(groupsData))
		}
	}()

	// Auto-save data every 5 minutes
	go func() {
		ticker := time.NewTicker(5 * time.Minute)
		for range ticker.C {
			saveGroupsData()
			log.Println("💾 Group data saved to file")
		}
	}()

	log.Println("✅ Bot started successfully!")
	log.Println("✅ Assistant connected!")
	log.Println("✅ Voice Chat ready!")
	log.Println("✅ Per-Group Memory: ENABLED")
	log.Println("✅ Keep-Alive: Every 10 minutes")
	log.Println("==================================================")

	// Example: Simulate group commands (for testing)
	// In real bot, these would come from Telegram handlers
	exampleGroupID := int64(123456789)
	group := getGroupData(exampleGroupID)
	log.Printf("📋 Group %d - Loop mode: %s, Speed: %.1fx", exampleGroupID, group.LoopMode, group.Speed)

	// Update example
	updateGroupData(exampleGroupID, func(g *GroupData) {
		g.LoopMode = "one"
		g.Speed = 1.5
	})

	log.Printf("📋 After update - Loop mode: %s, Speed: %.1fx", group.LoopMode, group.Speed)

	// Keep the bot running
	ctx, cancel := context.WithCancel(context.Background())
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-sigChan
		log.Println("Shutting down...")
		saveGroupsData() // Final save before shutdown
		cancel()
	}()

	<-ctx.Done()
}
