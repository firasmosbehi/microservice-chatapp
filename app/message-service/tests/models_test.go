package main

import (
	"testing"
	"time"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockDatabase is a mock implementation of the database interface
type MockDatabase struct {
	mock.Mock
}

func (m *MockDatabase) CreateMessage(message *Message) error {
	args := m.Called(message)
	return args.Error(0)
}

func (m *MockDatabase) GetMessagesByRoom(roomID string, limit, offset int) ([]Message, error) {
	args := m.Called(roomID, limit, offset)
	return args.Get(0).([]Message), args.Error(1)
}

func (m *MockDatabase) GetMessageByID(id uint) (*Message, error) {
	args := m.Called(id)
	return args.Get(0).(*Message), args.Error(1)
}

func (m *MockDatabase) UpdateMessageReadStatus(messageID uint, userID uint) error {
	args := m.Called(messageID, userID)
	return args.Error(0)
}

func (m *MockDatabase) DeleteMessage(id uint) error {
	args := m.Called(id)
	return args.Error(0)
}

func (m *MockDatabase) CreateRoom(room *Room) error {
	args := m.Called(room)
	return args.Error(0)
}

func (m *MockDatabase) GetRooms() ([]Room, error) {
	args := m.Called()
	return args.Get(0).([]Room), args.Error(1)
}

func (m *MockDatabase) GetUnreadCount(userID uint) (int64, error) {
	args := m.Called(userID)
	return args.Get(0).(int64), args.Error(1)
}

// TestMessageModel tests the Message struct and its methods
func TestMessageModel(t *testing.T) {
	now := time.Now()
	
	message := Message{
		Model:    gorm.Model{ID: 1},
		RoomID:   "test-room-123",
		SenderID: 42,
		Content:  "Hello, world!",
		ReadBy:   []uint{1, 2, 3},
		CreatedAt: now,
		UpdatedAt: now,
	}

	assert.Equal(t, uint(1), message.ID)
	assert.Equal(t, "test-room-123", message.RoomID)
	assert.Equal(t, uint(42), message.SenderID)
	assert.Equal(t, "Hello, world!", message.Content)
	assert.Equal(t, 3, len(message.ReadBy))
	assert.Equal(t, now, message.CreatedAt)
	assert.Equal(t, now, message.UpdatedAt)
}

// TestRoomModel tests the Room struct and its methods
func TestRoomModel(t *testing.T) {
	now := time.Now()
	
	room := Room{
		Model:     gorm.Model{ID: 1},
		Name:      "Test Room",
		CreatorID: 42,
		Members:   []uint{1, 2, 3, 4},
		CreatedAt: now,
		UpdatedAt: now,
	}

	assert.Equal(t, uint(1), room.ID)
	assert.Equal(t, "Test Room", room.Name)
	assert.Equal(t, uint(42), room.CreatorID)
	assert.Equal(t, 4, len(room.Members))
	assert.Equal(t, now, room.CreatedAt)
	assert.Equal(t, now, room.UpdatedAt)
}

// TestMessageValidation tests message validation logic
func TestMessageValidation(t *testing.T) {
	tests := []struct {
		name          string
		message       Message
		expectValid   bool
		errorContains string
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
			expectValid:   false,
			errorContains: "content cannot be empty",
		},
		{
			name: "Empty room ID",
			message: Message{
				RoomID:   "",
				SenderID: 1,
				Content:  "Hello",
			},
			expectValid:   false,
			errorContains: "room ID cannot be empty",
		},
		{
			name: "Zero sender ID",
			message: Message{
				RoomID:   "test-room-123",
				SenderID: 0,
				Content:  "Hello",
			},
			expectValid:   false,
			errorContains: "sender ID must be greater than 0",
		},
		{
			name: "Content too long",
			message: Message{
				RoomID:   "test-room-123",
				SenderID: 1,
				Content:  string(make([]byte, 5001)), // 5001 characters
			},
			expectValid:   false,
			errorContains: "content too long",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := validateMessage(&tt.message)
			
			if tt.expectValid {
				assert.NoError(t, err)
			} else {
				assert.Error(t, err)
				assert.Contains(t, err.Error(), tt.errorContains)
			}
		})
	}
}

// TestRoomValidation tests room validation logic
func TestRoomValidation(t *testing.T) {
	tests := []struct {
		name          string
		room          Room
		expectValid   bool
		errorContains string
	}{
		{
			name: "Valid room",
			room: Room{
				Name:      "Test Room",
				CreatorID: 1,
			},
			expectValid: true,
		},
		{
			name: "Empty room name",
			room: Room{
				Name:      "",
				CreatorID: 1,
			},
			expectValid:   false,
			errorContains: "room name cannot be empty",
		},
		{
			name: "Name too long",
			room: Room{
				Name:      string(make([]byte, 101)), // 101 characters
				CreatorID: 1,
			},
			expectValid:   false,
			errorContains: "room name too long",
		},
		{
			name: "Zero creator ID",
			room: Room{
				Name:      "Test Room",
				CreatorID: 0,
			},
			expectValid:   false,
			errorContains: "creator ID must be greater than 0",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := validateRoom(&tt.room)
			
			if tt.expectValid {
				assert.NoError(t, err)
			} else {
				assert.Error(t, err)
				assert.Contains(t, err.Error(), tt.errorContains)
			}
		})
	}
}

// TestMessageService tests the message service layer
func TestMessageService(t *testing.T) {
	mockDB := new(MockDatabase)
	service := &MessageService{db: mockDB}

	t.Run("CreateMessage", func(t *testing.T) {
		message := &Message{
			RoomID:   "test-room",
			SenderID: 1,
			Content:  "Hello",
		}

		mockDB.On("CreateMessage", message).Return(nil)

		err := service.CreateMessage(message)
		assert.NoError(t, err)
		mockDB.AssertExpectations(t)
	})

	t.Run("GetMessagesByRoom", func(t *testing.T) {
		expectedMessages := []Message{
			{Model: gorm.Model{ID: 1}, Content: "Message 1"},
			{Model: gorm.Model{ID: 2}, Content: "Message 2"},
		}

		mockDB.On("GetMessagesByRoom", "test-room", 10, 0).Return(expectedMessages, nil)

		messages, err := service.GetMessagesByRoom("test-room", 10, 0)
		assert.NoError(t, err)
		assert.Equal(t, expectedMessages, messages)
		mockDB.AssertExpectations(t)
	})

	t.Run("GetMessageByID", func(t *testing.T) {
		expectedMessage := &Message{Model: gorm.Model{ID: 1}, Content: "Test message"}

		mockDB.On("GetMessageByID", uint(1)).Return(expectedMessage, nil)

		message, err := service.GetMessageByID(1)
		assert.NoError(t, err)
		assert.Equal(t, expectedMessage, message)
		mockDB.AssertExpectations(t)
	})

	t.Run("UpdateMessageReadStatus", func(t *testing.T) {
		mockDB.On("UpdateMessageReadStatus", uint(1), uint(2)).Return(nil)

		err := service.UpdateMessageReadStatus(1, 2)
		assert.NoError(t, err)
		mockDB.AssertExpectations(t)
	})

	t.Run("DeleteMessage", func(t *testing.T) {
		mockDB.On("DeleteMessage", uint(1)).Return(nil)

		err := service.DeleteMessage(1)
		assert.NoError(t, err)
		mockDB.AssertExpectations(t)
	})
}

// TestRoomService tests the room service layer
func TestRoomService(t *testing.T) {
	mockDB := new(MockDatabase)
	service := &RoomService{db: mockDB}

	t.Run("CreateRoom", func(t *testing.T) {
		room := &Room{
			Name:      "Test Room",
			CreatorID: 1,
		}

		mockDB.On("CreateRoom", room).Return(nil)

		err := service.CreateRoom(room)
		assert.NoError(t, err)
		mockDB.AssertExpectations(t)
	})

	t.Run("GetRooms", func(t *testing.T) {
		expectedRooms := []Room{
			{Model: gorm.Model{ID: 1}, Name: "Room 1"},
			{Model: gorm.Model{ID: 2}, Name: "Room 2"},
		}

		mockDB.On("GetRooms").Return(expectedRooms, nil)

		rooms, err := service.GetRooms()
		assert.NoError(t, err)
		assert.Equal(t, expectedRooms, rooms)
		mockDB.AssertExpectations(t)
	})

	t.Run("GetUnreadCount", func(t *testing.T) {
		mockDB.On("GetUnreadCount", uint(1)).Return(int64(5), nil)

		count, err := service.GetUnreadCount(1)
		assert.NoError(t, err)
		assert.Equal(t, int64(5), count)
		mockDB.AssertExpectations(t)
	})
}

// TestMessageSorting tests message sorting functionality
func TestMessageSorting(t *testing.T) {
	messages := []Message{
		{
			Model:     gorm.Model{ID: 1},
			CreatedAt: time.Now().Add(-2 * time.Hour),
			Content:   "Oldest message",
		},
		{
			Model:     gorm.Model{ID: 2},
			CreatedAt: time.Now().Add(-1 * time.Hour),
			Content:   "Middle message",
		},
		{
			Model:     gorm.Model{ID: 3},
			CreatedAt: time.Now(),
			Content:   "Newest message",
		},
	}

	// Sort messages by creation time (ascending)
	sorted := sortByTimestamp(messages, false)
	
	assert.Equal(t, uint(1), sorted[0].ID)
	assert.Equal(t, uint(2), sorted[1].ID)
	assert.Equal(t, uint(3), sorted[2].ID)

	// Sort messages by creation time (descending)
	sortedDesc := sortByTimestamp(messages, true)
	
	assert.Equal(t, uint(3), sortedDesc[0].ID)
	assert.Equal(t, uint(2), sortedDesc[1].ID)
	assert.Equal(t, uint(1), sortedDesc[2].ID)
}

// TestMessageFiltering tests message filtering functionality
func TestMessageFiltering(t *testing.T) {
	messages := []Message{
		{Model: gorm.Model{ID: 1}, SenderID: 1, Content: "Message from user 1"},
		{Model: gorm.Model{ID: 2}, SenderID: 2, Content: "Message from user 2"},
		{Model: gorm.Model{ID: 3}, SenderID: 1, Content: "Another message from user 1"},
		{Model: gorm.Model{ID: 4}, SenderID: 3, Content: "Message from user 3"},
	}

	// Filter by sender ID
	filtered := filterBySender(messages, 1)
	assert.Equal(t, 2, len(filtered))
	assert.Equal(t, uint(1), filtered[0].SenderID)
	assert.Equal(t, uint(1), filtered[1].SenderID)

	// Filter by content substring
	filteredContent := filterByContent(messages, "user 2")
	assert.Equal(t, 1, len(filteredContent))
	assert.Equal(t, "Message from user 2", filteredContent[0].Content)
}

// Benchmark tests
func BenchmarkMessageCreation(b *testing.B) {
	for i := 0; i < b.N; i++ {
		message := Message{
			RoomID:    "benchmark-room",
			SenderID:  uint(i % 1000),
			Content:   "Benchmark message content",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
		_ = validateMessage(&message)
	}
}

func BenchmarkMessageSorting(b *testing.B) {
	// Create test messages
	messages := make([]Message, 1000)
	for i := 0; i < 1000; i++ {
		messages[i] = Message{
			Model:     gorm.Model{ID: uint(i)},
			CreatedAt: time.Now().Add(time.Duration(i) * time.Minute),
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		sortByTimestamp(messages, false)
	}
}

// Example tests for documentation
func ExampleMessage_validation() {
	message := Message{
		RoomID:   "test-room",
		SenderID: 1,
		Content:  "Hello world",
	}
	
	err := validateMessage(&message)
	
	if err == nil {
		// Message is valid
	}
}