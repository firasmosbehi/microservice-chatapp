import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from main import app, chat_rooms, messages, active_connections
from pydantic import ValidationError

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup():
    """Clean up global state before each test"""
    chat_rooms.clear()
    messages.clear()
    active_connections.clear()

class TestChatModels:
    def test_create_room_request_validation(self):
        """Test CreateRoomRequest model validation"""
        from main import CreateRoomRequest
        
        # Valid request
        valid_request = CreateRoomRequest(
            name="Test Room",
            creator_id=1,
            description="A test room",
            is_private=False
        )
        assert valid_request.name == "Test Room"
        assert valid_request.creator_id == 1
        
        # Test optional fields
        minimal_request = CreateRoomRequest(
            name="Minimal Room",
            creator_id=2
        )
        assert minimal_request.description is None
        assert minimal_request.is_private is False
    
    def test_invalid_create_room_request(self):
        """Test CreateRoomRequest validation errors"""
        from main import CreateRoomRequest
        
        # Missing required fields should raise ValidationError
        with pytest.raises(ValidationError):
            CreateRoomRequest(name="Only Name")  # Missing creator_id
            
        with pytest.raises(ValidationError):
            CreateRoomRequest(creator_id=1)  # Missing name

    def test_join_room_request_validation(self):
        """Test JoinRoomRequest model validation"""
        from main import JoinRoomRequest
        
        valid_request = JoinRoomRequest(
            user_id=123,
            username="testuser"
        )
        assert valid_request.user_id == 123
        assert valid_request.username == "testuser"
        
        # Test validation errors
        with pytest.raises(ValidationError):
            JoinRoomRequest(user_id=123)  # Missing username
            
        with pytest.raises(ValidationError):
            JoinRoomRequest(username="testuser")  # Missing user_id

    def test_message_request_validation(self):
        """Test MessageRequest model validation"""
        from main import MessageRequest
        
        valid_request = MessageRequest(
            room_id="room123",
            user_id=456,
            username="messager",
            content="Hello world"
        )
        assert valid_request.room_id == "room123"
        assert valid_request.content == "Hello world"
        assert valid_request.message_type == "text"  # Default value
        
        # Test with custom message type
        image_request = MessageRequest(
            room_id="room123",
            user_id=456,
            username="messager",
            content="image_data",
            message_type="image"
        )
        assert image_request.message_type == "image"

class TestChatAPIEndpoints:
    def test_health_check(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        
    def test_create_room(self):
        """Test room creation endpoint"""
        room_data = {
            "name": "Test Chat Room",
            "creator_id": 1,
            "description": "A test room for chatting"
        }
        
        response = client.post("/rooms", json=room_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["name"] == room_data["name"]
        assert data["creator_id"] == room_data["creator_id"]
        
        # Verify room was stored
        assert data["id"] in chat_rooms
        
    def test_create_room_missing_fields(self):
        """Test room creation with missing required fields"""
        # Missing creator_id
        invalid_data = {"name": "Incomplete Room"}
        response = client.post("/rooms", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
    def test_get_rooms(self):
        """Test getting all rooms"""
        # Create a room first
        room_data = {"name": "Test Room", "creator_id": 1}
        client.post("/rooms", json=room_data)
        
        response = client.get("/rooms")
        assert response.status_code == 200
        
        rooms = response.json()
        assert isinstance(rooms, list)
        assert len(rooms) >= 1
        
    def test_get_specific_room(self):
        """Test getting a specific room"""
        # Create a room
        room_data = {"name": "Specific Room", "creator_id": 1}
        create_response = client.post("/rooms", json=room_data)
        room_id = create_response.json()["id"]
        
        # Get the room
        response = client.get(f"/rooms/{room_id}")
        assert response.status_code == 200
        
        room = response.json()
        assert room["id"] == room_id
        assert room["name"] == "Specific Room"
        
    def test_get_nonexistent_room(self):
        """Test getting a room that doesn't exist"""
        response = client.get("/rooms/nonexistent123")
        assert response.status_code == 404
        
    def test_join_room(self):
        """Test joining a room"""
        # Create a room
        room_data = {"name": "Join Test Room", "creator_id": 1}
        create_response = client.post("/rooms", json=room_data)
        room_id = create_response.json()["id"]
        
        # Join the room
        join_data = {"user_id": 123, "username": "testuser"}
        response = client.post(f"/rooms/{room_id}/join", json=join_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["message"] == "Successfully joined room"
        assert result["room"]["member_count"] == 1
        
    def test_join_room_nonexistent(self):
        """Test joining a nonexistent room"""
        join_data = {"user_id": 123, "username": "testuser"}
        response = client.post("/rooms/nonexistent/join", json=join_data)
        assert response.status_code == 404
        
    def test_send_message(self):
        """Test sending a message"""
        # Create room and join
        room_data = {"name": "Message Test Room", "creator_id": 1}
        create_response = client.post("/rooms", json=room_data)
        room_id = create_response.json()["id"]
        
        join_data = {"user_id": 123, "username": "sender"}
        client.post(f"/rooms/{room_id}/join", json=join_data)
        
        # Send message
        message_data = {
            "room_id": room_id,
            "user_id": 123,
            "username": "sender",
            "content": "Hello everyone!"
        }
        
        response = client.post("/messages", json=message_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "message_id" in result
        
        # Verify message was stored
        assert room_id in messages
        assert len(messages[room_id]) >= 1
        
    def test_get_room_messages(self):
        """Test retrieving room messages"""
        # Create room, join, and send messages
        room_data = {"name": "History Test Room", "creator_id": 1}
        create_response = client.post("/rooms", json=room_data)
        room_id = create_response.json()["id"]
        
        # Send multiple messages
        for i in range(3):
            message_data = {
                "room_id": room_id,
                "user_id": 123,
                "username": "user",
                "content": f"Message {i}"
            }
            client.post("/messages", json=message_data)
        
        # Get messages
        response = client.get(f"/rooms/{room_id}/messages")
        assert response.status_code == 200
        
        retrieved_messages = response.json()
        assert isinstance(retrieved_messages, list)
        assert len(retrieved_messages) >= 3
        
        # Check message structure
        for msg in retrieved_messages[-3:]:  # Last 3 messages
            assert "id" in msg
            assert "content" in msg
            assert "username" in msg
            assert "timestamp" in msg

    def test_leave_room(self):
        """Test leaving a room"""
        # Create room and join
        room_data = {"name": "Leave Test Room", "creator_id": 1}
        create_response = client.post("/rooms", json=room_data)
        room_id = create_response.json()["id"]
        
        join_data = {"user_id": 123, "username": "leaver"}
        client.post(f"/rooms/{room_id}/join", json=join_data)
        
        # Leave room
        response = client.post(f"/rooms/{room_id}/leave", json=join_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["message"] == "Successfully left room"
        assert result["room"]["member_count"] == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])