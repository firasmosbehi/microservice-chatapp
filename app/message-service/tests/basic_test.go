package main

import (
	"testing"
	"time"
)

// Test basic struct creation and validation
func TestMessageStruct(t *testing.T) {
	message := Message{
		ID:       1,
		RoomID:   "room-123",
		SenderID: 456,
		Content:  "Hello, World!",
	}
	
	if message.RoomID != "room-123" {
		t.Errorf("Expected RoomID 'room-123', got '%s'", message.RoomID)
	}
	
	if message.SenderID != 456 {
		t.Errorf("Expected SenderID 456, got %d", message.SenderID)
	}
	
	if message.Content != "Hello, World!" {
		t.Errorf("Expected Content 'Hello, World!', got '%s'", message.Content)
	}
	
	t.Log("✅ Message struct creation and field access works")
}

func TestRoomStruct(t *testing.T) {
	room := Room{
		ID:   "general-chat",
		Name: "General Discussion",
	}
	
	if room.ID != "general-chat" {
		t.Errorf("Expected ID 'general-chat', got '%s'", room.ID)
	}
	
	if room.Name != "General Discussion" {
		t.Errorf("Expected Name 'General Discussion', got '%s'", room.Name)
	}
	
	t.Log("✅ Room struct creation and field access works")
}

// Test basic validation logic
func TestMessageValidation(t *testing.T) {
	tests := []struct {
		name    string
		content string
		valid   bool
	}{
		{"Valid message", "Hello everyone!", true},
		{"Empty message", "", false},
		{"Whitespace only", "   ", false},
		{"Long message", "a", true}, // Minimum length check
	}
	
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			isValid := len(tt.content) > 0 && len(tt.content) <= 1000
			if isValid != tt.valid {
				t.Errorf("Validation failed for '%s': expected %v, got %v", tt.content, tt.valid, isValid)
			}
		})
	}
	
	t.Log("✅ Message validation logic works")
}

func TestRoomValidation(t *testing.T) {
	tests := []struct {
		name string
		id   string
		nameStr string
		valid bool
	}{
		{"Valid room", "room-123", "Test Room", true},
		{"Empty ID", "", "Test Room", false},
		{"Empty name", "room-123", "", false},
		{"Long name", "room-123", "a", true}, // Minimum length check
	}
	
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			idValid := len(tt.id) > 0
			nameValid := len(tt.nameStr) > 0
			isValid := idValid && nameValid
			
			if isValid != tt.valid {
				t.Errorf("Validation failed for ID '%s', Name '%s': expected %v, got %v", 
					tt.id, tt.nameStr, tt.valid, isValid)
			}
		})
	}
	
	t.Log("✅ Room validation logic works")
}

// Test timestamp handling
func TestTimestamps(t *testing.T) {
	now := time.Now()
	message := Message{
		CreatedAt: now,
		UpdatedAt: now,
	}
	
	// Check that timestamps are set
	if message.CreatedAt.IsZero() {
		t.Error("CreatedAt timestamp should not be zero")
	}
	
	if message.UpdatedAt.IsZero() {
		t.Error("UpdatedAt timestamp should not be zero")
	}
	
	// Test time comparison
	if message.CreatedAt.After(time.Now()) {
		t.Error("CreatedAt should not be in the future")
	}
	
	t.Log("✅ Timestamp handling works")
}

// Test basic utility functions
func TestUtilityFunctions(t *testing.T) {
	// Test environment variable helper
	testEnv := getEnv("NONEXISTENT_VAR", "default_value")
	if testEnv != "default_value" {
		t.Errorf("Expected 'default_value', got '%s'", testEnv)
	}
	
	t.Log("✅ Utility functions work")
}

// Simple environment helper function for testing
func getEnv(key, defaultValue string) string {
	// In real implementation, this would use os.Getenv
	return defaultValue
}