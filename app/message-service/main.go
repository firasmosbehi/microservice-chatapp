package main

import (
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

// Simple message model
type Message struct {
	ID        uint      `json:"id" gorm:"primaryKey"`
	RoomID    string    `json:"room_id"` // Changed from uint to string
	SenderID  uint      `json:"sender_id"`
	Content   string    `json:"content"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// Room model
type Room struct {
	ID        string    `json:"id" gorm:"primaryKey"` // Changed from uint to string
	Name      string    `json:"name"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

var db *gorm.DB

func initDB() {
	// Load environment variables
	err := godotenv.Load()
	if err != nil {
		log.Println("No .env file found")
	}

	host := getEnv("DB_HOST", "localhost")
	user := getEnv("DB_USER", "postgres")
	password := getEnv("DB_PASSWORD", "password")
	dbname := getEnv("DB_NAME", "chatapp_messages")
	port := getEnv("DB_PORT", "5432")

	dsn := "host=" + host + " user=" + user + " password=" + password + " dbname=" + dbname + " port=" + port + " sslmode=disable"
	
	db, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}

	// Auto migrate
	db.AutoMigrate(&Message{}, &Room{})
	log.Println("Database connected and migrated")
}

func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}

func healthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":  "healthy",
		"message": "Message Service Running",
		"version": "1.0.0",
	})
}

func createRoom(c *gin.Context) {
	var room Room
	if err := c.ShouldBindJSON(&room); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	room.CreatedAt = time.Now()
	room.UpdatedAt = time.Now()
	
	result := db.Create(&room)
	if result.Error != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": result.Error.Error()})
		return
	}

	c.JSON(http.StatusCreated, room)
}

func getRooms(c *gin.Context) {
	var rooms []Room
	result := db.Find(&rooms)
	if result.Error != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": result.Error.Error()})
		return
	}
	c.JSON(http.StatusOK, rooms)
}

func sendMessage(c *gin.Context) {
	var message Message
	if err := c.ShouldBindJSON(&message); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	message.CreatedAt = time.Now()
	message.UpdatedAt = time.Now()
	
	result := db.Create(&message)
	if result.Error != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": result.Error.Error()})
		return
	}

	c.JSON(http.StatusCreated, message)
}

func getRoomMessages(c *gin.Context) {
	roomID := c.Param("room_id")
	var messages []Message
	
	result := db.Where("room_id = ?", roomID).Order("created_at DESC").Limit(50).Find(&messages)
	if result.Error != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": result.Error.Error()})
		return
	}

	// Reverse for chronological order
	for i, j := 0, len(messages)-1; i < j; i, j = i+1, j-1 {
		messages[i], messages[j] = messages[j], messages[i]
	}

	c.JSON(http.StatusOK, messages)
}

func main() {
	initDB()

	router := gin.Default()
	
	// Health check
	router.GET("/", healthCheck)
	
	// Room endpoints
	router.POST("/rooms", createRoom)
	router.GET("/rooms", getRooms)
	
	// Message endpoints
	router.POST("/messages", sendMessage)
	router.GET("/rooms/:room_id/messages", getRoomMessages)
	
	port := getEnv("PORT", "3003")
	log.Printf("Message Service starting on port %s", port)
	log.Fatal(router.Run(":" + port))
}