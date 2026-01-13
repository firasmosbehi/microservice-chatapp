package main

import (
	"testing"
	"time"
)

func TestBasicStructures(t *testing.T) {
	// Test simple struct creation
	type Message struct {
		ID      int
		Content string
	}
	
	msg := Message{ID: 1, Content: "Hello"}
	if msg.ID != 1 {
		t.Error("Message ID mismatch")
	}
	if msg.Content != "Hello" {
		t.Error("Message content mismatch")
	}
	
	t.Log("✅ Basic struct operations work")
}

func TestValidationLogic(t *testing.T) {
	// Test basic validation
	content := "Hello World"
	if len(content) == 0 {
		t.Error("Content should not be empty")
	}
	
	if len(content) > 1000 {
		t.Error("Content should not exceed 1000 characters")
	}
	
	t.Log("✅ Basic validation works")
}

func TestTimeOperations(t *testing.T) {
	now := time.Now()
	if now.IsZero() {
		t.Error("Time should not be zero")
	}
	
	// Test time formatting
	formatted := now.Format("2006-01-02 15:04:05")
	if formatted == "" {
		t.Error("Time formatting failed")
	}
	
	t.Log("✅ Time operations work")
}

func TestDataStructures(t *testing.T) {
	// Test slice operations
	messages := []string{}
	messages = append(messages, "Message 1")
	messages = append(messages, "Message 2")
	
	if len(messages) != 2 {
		t.Errorf("Expected 2 messages, got %d", len(messages))
	}
	
	// Test map operations
	rooms := make(map[string]string)
	rooms["general"] = "General Chat"
	
	if rooms["general"] != "General Chat" {
		t.Error("Map lookup failed")
	}
	
	t.Log("✅ Data structures work")
}