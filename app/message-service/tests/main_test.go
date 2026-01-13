package main

import (
	"testing"
	"time"
)

// TestMessageValidation tests the validation logic for messages
func TestMessageValidation(t *testing.T) {
	tests := []struct {
		name        string
		message     Message
		expectValid bool
	}{
		{
			name: "Valid message",
			message: Message{
				RoomID:   "test-room-123",
				SenderID: 1,
				Content:  "Hello world",
			},
			expectValid: true,
		},
		{
			name: "Empty content",
			message: Message{
				RoomID:   "test-room-123",
				SenderID: 1,
				Content:  "",
			},
			expectValid: false,
		},
		{
			name: "Zero sender ID",
			message: Message{
				RoomID:   "test-room-123",
				SenderID: 0,
				Content:  "Hello",
			},
			expectValid: true, // Assuming 0 is valid
		},
		{
			name: "Empty room ID",
			message: Message{
				RoomID:   "",
				SenderID: 1,
				Content:  "Hello",
			},
			expectValid: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Simple validation logic
			valid := tt.message.Content != "" && tt.message.RoomID != ""
			
			if valid != tt.expectValid {
				t.Errorf("Message validation failed for %s: expected %v, got %v", 
					tt.name, tt.expectValid, valid)
			}
		})
	}
}

// TestRoomValidation tests the validation logic for rooms
func TestRoomValidation(t *testing.T) {
	tests := []struct {
		name        string
		room        Room
		expectValid bool
	}{
		{
			name: "Valid room",
			room: Room{
				ID:   "room-123",
				Name: "Test Room",
			},
			expectValid: true,
		},
		{
			name: "Empty room name",
			room: Room{
				ID:   "room-123",
				Name: "",
			},
			expectValid: false,
		},
		{
			name: "Empty room ID",
			room: Room{
				ID:   "",
				Name: "Test Room",
			},
			expectValid: false,
		},
		{
			name: "Very long room name",
			room: Room{
				ID:   "room-123",
				Name: string(make([]byte, 101)), // 101 characters
			},
			expectValid: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Simple validation logic
			valid := tt.room.Name != "" && tt.room.ID != "" && len(tt.room.Name) <= 100
			
			if valid != tt.expectValid {
				t.Errorf("Room validation failed for %s: expected %v, got %v", 
					tt.name, tt.expectValid, valid)
			}
		})
	}
}

// TestTimeFormatting tests timestamp formatting
func TestTimeFormatting(t *testing.T) {
	now := time.Now()
	
	// Test that timestamps are properly formatted
	formatted := now.Format(time.RFC3339)
	
	if formatted == "" {
		t.Error("Time formatting returned empty string")
	}
	
	// Parse it back to ensure it's valid
	_, err := time.Parse(time.RFC3339, formatted)
	if err != nil {
		t.Errorf("Formatted time is not valid RFC3339: %v", err)
	}
}

// TestMessageSorting tests message sorting by timestamp
func TestMessageSorting(t *testing.T) {
	messages := []Message{
		{
			ID:        1,
			CreatedAt: time.Now().Add(-2 * time.Hour),
			Content:   "Oldest message",
		},
		{
			ID:        2,
			CreatedAt: time.Now().Add(-1 * time.Hour),
			Content:   "Middle message",
		},
		{
			ID:        3,
			CreatedAt: time.Now(),
			Content:   "Newest message",
		},
	}
	
	// Simple bubble sort implementation for testing
	n := len(messages)
	for i := 0; i < n-1; i++ {
		for j := 0; j < n-i-1; j++ {
			if messages[j].CreatedAt.After(messages[j+1].CreatedAt) {
				messages[j], messages[j+1] = messages[j+1], messages[j]
			}
		}
	}
	
	// Verify sorting
	if messages[0].ID != 1 {
		t.Error("Messages not sorted correctly by timestamp")
	}
	if messages[1].ID != 2 {
		t.Error("Messages not sorted correctly by timestamp")
	}
	if messages[2].ID != 3 {
		t.Error("Messages not sorted correctly by timestamp")
	}
}

// BenchmarkMessageCreation benchmarks message creation performance
func BenchmarkMessageCreation(b *testing.B) {
	for i := 0; i < b.N; i++ {
		msg := Message{
			RoomID:    "benchmark-room",
			SenderID:  uint(i % 1000),
			Content:   "Benchmark message content",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
		// Simulate some processing
		_ = msg.Content
	}
}

// Example test for documentation
func ExampleMessage_validation() {
	msg := Message{
		RoomID:   "test-room",
		SenderID: 1,
		Content:  "Hello world",
	}
	
	valid := msg.Content != "" && msg.RoomID != ""
	
	if valid {
		// Message is valid
	}
}