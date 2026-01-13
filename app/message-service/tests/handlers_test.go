package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockMessageService is a mock implementation of the MessageService interface
type MockMessageService struct {
	mock.Mock
}

func (m *MockMessageService) CreateMessage(message *Message) error {
	args := m.Called(message)
	return args.Error(0)
}

func (m *MockMessageService) GetMessagesByRoom(roomID string, limit, offset int) ([]Message, error) {
	args := m.Called(roomID, limit, offset)
	return args.Get(0).([]Message), args.Error(1)
}

func (m *MockMessageService) GetMessageByID(id uint) (*Message, error) {
	args := m.Called(id)
	return args.Get(0).(*Message), args.Error(1)
}

func (m *MockMessageService) UpdateMessageReadStatus(messageID uint, userID uint) error {
	args := m.Called(messageID, userID)
	return args.Error(0)
}

func (m *MockMessageService) DeleteMessage(id uint) error {
	args := m.Called(id)
	return args.Error(0)
}

// MockRoomService is a mock implementation of the RoomService interface
type MockRoomService struct {
	mock.Mock
}

func (m *MockRoomService) CreateRoom(room *Room) error {
	args := m.Called(room)
	return args.Error(0)
}

func (m *MockRoomService) GetRooms() ([]Room, error) {
	args := m.Called()
	return args.Get(0).([]Room), args.Error(1)
}

func (m *MockRoomService) GetUnreadCount(userID uint) (int64, error) {
	args := m.Called(userID)
	return args.Get(0).(int64), args.Error(1)
}

func setupRouter() *gin.Engine {
	gin.SetMode(gin.TestMode)
	router := gin.New()
	return router
}

func TestMessageHandlers(t *testing.T) {
	mockMsgService := new(MockMessageService)
	mockRoomService := new(MockRoomService)
	
	// Create handlers with mock services
	handlers := &Handlers{
		MessageService: mockMsgService,
		RoomService:    mockRoomService,
	}

	router := setupRouter()
	
	// Setup routes
	api := router.Group("/api")
	{
		messages := api.Group("/messages")
		{
			messages.POST("", handlers.CreateMessage)
			messages.GET("/room/:room_id", handlers.GetMessagesByRoom)
			messages.GET("/:id", handlers.GetMessage)
			messages.PUT("/:id/read", handlers.UpdateReadStatus)
			messages.DELETE("/:id", handlers.DeleteMessage)
		}
		
		rooms := api.Group("/rooms")
		{
			rooms.POST("", handlers.CreateRoom)
			rooms.GET("", handlers.GetRooms)
			rooms.GET("/unread/:user_id", handlers.GetUnreadCount)
		}
	}

	t.Run("CreateMessage_Success", func(t *testing.T) {
		message := MessageRequest{
			RoomID:   "test-room-123",
			SenderID: 1,
			Content:  "Hello, world!",
		}
		
		jsonBytes, _ := json.Marshal(message)
		req, _ := http.NewRequest("POST", "/api/messages", bytes.NewBuffer(jsonBytes))
		req.Header.Set("Content-Type", "application/json")
		
		// Mock service call
		mockMsgService.On("CreateMessage", mock.AnythingOfType("*main.Message")).Return(nil)
		
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusCreated, w.Code)
		
		var response map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.Equal(t, "Message created successfully", response["message"])
		
		mockMsgService.AssertExpectations(t)
	})

	t.Run("CreateMessage_InvalidJSON", func(t *testing.T) {
		req, _ := http.NewRequest("POST", "/api/messages", bytes.NewBuffer([]byte("invalid json")))
		req.Header.Set("Content-Type", "application/json")
		
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("CreateMessage_ValidationError", func(t *testing.T) {
		message := MessageRequest{
			RoomID:   "", // Empty room ID should cause validation error
			SenderID: 1,
			Content:  "Hello",
		}
		
		jsonBytes, _ := json.Marshal(message)
		req, _ := http.NewRequest("POST", "/api/messages", bytes.NewBuffer(jsonBytes))
		req.Header.Set("Content-Type", "application/json")
		
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("GetMessagesByRoom_Success", func(t *testing.T) {
		expectedMessages := []Message{
			{Model: gorm.Model{ID: 1}, Content: "Message 1"},
			{Model: gorm.Model{ID: 2}, Content: "Message 2"},
		}
		
		// Mock service call
		mockMsgService.On("GetMessagesByRoom", "test-room", 50, 0).Return(expectedMessages, nil)
		
		req, _ := http.NewRequest("GET", "/api/messages/room/test-room?limit=50&offset=0", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response MessagesResponse
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.Equal(t, 2, len(response.Messages))
		
		mockMsgService.AssertExpectations(t)
	})

	t.Run("GetMessage_Success", func(t *testing.T) {
		expectedMessage := &Message{Model: gorm.Model{ID: 1}, Content: "Test message"}
		
		// Mock service call
		mockMsgService.On("GetMessageByID", uint(1)).Return(expectedMessage, nil)
		
		req, _ := http.NewRequest("GET", "/api/messages/1", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response MessageResponse
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.Equal(t, "Test message", response.Message.Content)
		
		mockMsgService.AssertExpectations(t)
	})

	t.Run("GetMessage_NotFound", func(t *testing.T) {
		// Mock service call returning error
		mockMsgService.On("GetMessageByID", uint(999)).Return((*Message)(nil), gorm.ErrRecordNotFound)
		
		req, _ := http.NewRequest("GET", "/api/messages/999", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusNotFound, w.Code)
		
		mockMsgService.AssertExpectations(t)
	})

	t.Run("UpdateReadStatus_Success", func(t *testing.T) {
		// Mock service call
		mockMsgService.On("UpdateMessageReadStatus", uint(1), uint(2)).Return(nil)
		
		updateReq := UpdateReadStatusRequest{UserID: 2}
		jsonBytes, _ := json.Marshal(updateReq)
		
		req, _ := http.NewRequest("PUT", "/api/messages/1/read", bytes.NewBuffer(jsonBytes))
		req.Header.Set("Content-Type", "application/json")
		
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.Equal(t, "Read status updated", response["message"])
		
		mockMsgService.AssertExpectations(t)
	})

	t.Run("DeleteMessage_Success", func(t *testing.T) {
		// Mock service call
		mockMsgService.On("DeleteMessage", uint(1)).Return(nil)
		
		req, _ := http.NewRequest("DELETE", "/api/messages/1", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.Equal(t, "Message deleted", response["message"])
		
		mockMsgService.AssertExpectations(t)
	})
}

func TestRoomHandlers(t *testing.T) {
	mockMsgService := new(MockMessageService)
	mockRoomService := new(MockRoomService)
	
	handlers := &Handlers{
		MessageService: mockMsgService,
		RoomService:    mockRoomService,
	}

	router := setupRouter()
	
	// Setup room routes
	api := router.Group("/api")
	rooms := api.Group("/rooms")
	{
		rooms.POST("", handlers.CreateRoom)
		rooms.GET("", handlers.GetRooms)
		rooms.GET("/unread/:user_id", handlers.GetUnreadCount)
	}

	t.Run("CreateRoom_Success", func(t *testing.T) {
		room := RoomRequest{
			Name:      "Test Room",
			CreatorID: 1,
		}
		
		jsonBytes, _ := json.Marshal(room)
		req, _ := http.NewRequest("POST", "/api/rooms", bytes.NewBuffer(jsonBytes))
		req.Header.Set("Content-Type", "application/json")
		
		// Mock service call
		mockRoomService.On("CreateRoom", mock.AnythingOfType("*main.Room")).Return(nil)
		
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusCreated, w.Code)
		
		var response map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.Equal(t, "Room created successfully", response["message"])
		
		mockRoomService.AssertExpectations(t)
	})

	t.Run("GetRooms_Success", func(t *testing.T) {
		expectedRooms := []Room{
			{Model: gorm.Model{ID: 1}, Name: "Room 1"},
			{Model: gorm.Model{ID: 2}, Name: "Room 2"},
		}
		
		// Mock service call
		mockRoomService.On("GetRooms").Return(expectedRooms, nil)
		
		req, _ := http.NewRequest("GET", "/api/rooms", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response RoomsResponse
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.Equal(t, 2, len(response.Rooms))
		
		mockRoomService.AssertExpectations(t)
	})

	t.Run("GetUnreadCount_Success", func(t *testing.T) {
		// Mock service call
		mockRoomService.On("GetUnreadCount", uint(1)).Return(int64(5), nil)
		
		req, _ := http.NewRequest("GET", "/api/rooms/unread/1", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response UnreadCountResponse
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.Equal(t, int64(5), response.Count)
		
		mockRoomService.AssertExpectations(t)
	})
}

func TestMiddleware(t *testing.T) {
	router := setupRouter()
	
	// Test CORS middleware
	router.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")
		
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		
		c.Next()
	})
	
	router.GET("/test", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "success"})
	})

	t.Run("CORSMiddleware", func(t *testing.T) {
		req, _ := http.NewRequest("OPTIONS", "/test", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusNoContent, w.Code)
		assert.Equal(t, "*", w.Header().Get("Access-Control-Allow-Origin"))
	})

	t.Run("CORSPreflight", func(t *testing.T) {
		req, _ := http.NewRequest("GET", "/test", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		assert.Equal(t, "*", w.Header().Get("Access-Control-Allow-Origin"))
	})
}

func TestErrorHandling(t *testing.T) {
	mockMsgService := new(MockMessageService)
	mockRoomService := new(MockRoomService)
	
	handlers := &Handlers{
		MessageService: mockMsgService,
		RoomService:    mockRoomService,
	}

	router := setupRouter()
	router.POST("/api/messages", handlers.CreateMessage)

	t.Run("DatabaseError", func(t *testing.T) {
		message := MessageRequest{
			RoomID:   "test-room",
			SenderID: 1,
			Content:  "Hello",
		}
		
		jsonBytes, _ := json.Marshal(message)
		req, _ := http.NewRequest("POST", "/api/messages", bytes.NewBuffer(jsonBytes))
		req.Header.Set("Content-Type", "application/json")
		
		// Mock service call returning database error
		mockMsgService.On("CreateMessage", mock.AnythingOfType("*main.Message")).Return(gorm.ErrInvalidDB)
		
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusInternalServerError, w.Code)
		
		var response map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.Equal(t, "Database error occurred", response["error"])
		
		mockMsgService.AssertExpectations(t)
	})

	t.Run("ValidationError", func(t *testing.T) {
		invalidMessage := MessageRequest{
			RoomID:   "", // Invalid: empty room ID
			SenderID: 1,
			Content:  "Hello",
		}
		
		jsonBytes, _ := json.Marshal(invalidMessage)
		req, _ := http.NewRequest("POST", "/api/messages", bytes.NewBuffer(jsonBytes))
		req.Header.Set("Content-Type", "application/json")
		
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusBadRequest, w.Code)
		
		var response map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.Contains(t, response["error"], "validation failed")
	})
}