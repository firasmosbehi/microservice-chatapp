"""
Unit tests for Chat Service WebSocket functionality
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect
from main import app, chat_rooms, messages, active_connections

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture(autouse=True)
def cleanup():
    """Clean up global state before each test"""
    chat_rooms.clear()
    messages.clear()
    active_connections.clear()

class TestWebSocketConnections:
    """Test WebSocket connection handling"""
    
    @pytest.mark.asyncio
    async def test_websocket_connect_and_disconnect(self, client):
        """Test basic WebSocket connection and disconnection"""
        with client.websocket_connect("/ws/test-room") as websocket:
            # Send join message
            join_message = {
                "type": "join",
                "user_id": 1,
                "username": "testuser"
            }
            websocket.send_text(json.dumps(join_message))
            
            # Receive welcome message
            data = websocket.receive_text()
            response = json.loads(data)
            assert response["type"] == "welcome"
            assert response["message"] == "Connected to test-room"
            
            # Send disconnect message
            disconnect_message = {"type": "disconnect"}
            websocket.send_text(json.dumps(disconnect_message))

    @pytest.mark.asyncio
    async def test_multiple_users_in_same_room(self, client):
        """Test multiple users connecting to the same room"""
        # Connect first user
        with client.websocket_connect("/ws/test-room") as ws1:
            ws1.send_text(json.dumps({
                "type": "join",
                "user_id": 1,
                "username": "user1"
            }))
            ws1.receive_text()  # Welcome message
            
            # Connect second user
            with client.websocket_connect("/ws/test-room") as ws2:
                ws2.send_text(json.dumps({
                    "type": "join", 
                    "user_id": 2,
                    "username": "user2"
                }))
                ws2.receive_text()  # Welcome message
                
                # Both users should be in the room
                assert len(active_connections["test-room"]) == 2

    @pytest.mark.asyncio
    async def test_user_presence_tracking(self, client):
        """Test that user presence is properly tracked"""
        with client.websocket_connect("/ws/test-room") as websocket:
            # Join room
            websocket.send_text(json.dumps({
                "type": "join",
                "user_id": 1,
                "username": "presence_tester"
            }))
            websocket.receive_text()
            
            # Check that user is in presence tracking
            # This would require accessing internal state or mocking
            
    @pytest.mark.asyncio
    async def test_invalid_message_handling(self, client):
        """Test handling of invalid WebSocket messages"""
        with client.websocket_connect("/ws/test-room") as websocket:
            # Send malformed JSON
            websocket.send_text("invalid json")
            
            # Should handle gracefully - connection should remain open
            # Send valid message to confirm connection still works
            websocket.send_text(json.dumps({
                "type": "join",
                "user_id": 1,
                "username": "testuser"
            }))
            response = websocket.receive_text()
            assert "welcome" in response.lower()

class TestRoomManagement:
    """Test chat room creation and management"""
    
    def test_create_room_endpoint(self, client):
        """Test room creation via HTTP endpoint"""
        room_data = {
            "name": "Test Room",
            "creator_id": 1,
            "description": "A test room",
            "is_private": False
        }
        
        response = client.post("/rooms", json=room_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["name"] == room_data["name"]
        assert data["creator_id"] == room_data["creator_id"]

    def test_get_room_info(self, client):
        """Test retrieving room information"""
        # First create a room
        room_data = {"name": "Info Test", "creator_id": 1}
        create_response = client.post("/rooms", json=room_data)
        room_id = create_response.json()["id"]
        
        # Get room info
        response = client.get(f"/rooms/{room_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == room_id
        assert data["name"] == room_data["name"]

    def test_list_all_rooms(self, client):
        """Test listing all available rooms"""
        # Create multiple rooms
        rooms_data = [
            {"name": "Room 1", "creator_id": 1},
            {"name": "Room 2", "creator_id": 2},
            {"name": "Room 3", "creator_id": 3}
        ]
        
        for room_data in rooms_data:
            client.post("/rooms", json=room_data)
        
        # List all rooms
        response = client.get("/rooms")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 3
        room_names = [room["name"] for room in data]
        assert "Room 1" in room_names
        assert "Room 2" in room_names
        assert "Room 3" in room_names

    def test_join_and_leave_room(self, client):
        """Test joining and leaving rooms via HTTP"""
        # Create room
        room_data = {"name": "Join Test", "creator_id": 1}
        create_response = client.post("/rooms", json=room_data)
        room_id = create_response.json()["id"]
        
        # Join room
        join_data = {"user_id": 1, "username": "testuser"}
        join_response = client.post(f"/rooms/{room_id}/join", json=join_data)
        assert join_response.status_code == 200
        
        join_result = join_response.json()
        assert join_result["message"] == "Joined room successfully"
        assert join_result["room"]["member_count"] == 1
        
        # Leave room
        leave_response = client.post(f"/rooms/{room_id}/leave", json=join_data)
        assert leave_response.status_code == 200
        
        leave_result = leave_response.json()
        assert leave_result["message"] == "Left room successfully"

class TestMessaging:
    """Test message sending and receiving"""
    
    def test_send_message_http(self, client):
        """Test sending messages via HTTP endpoint"""
        # Create room first
        room_data = {"name": "Message Test", "creator_id": 1}
        room_response = client.post("/rooms", json=room_data)
        room_id = room_response.json()["id"]
        
        # Send message
        message_data = {
            "room_id": room_id,
            "user_id": 1,
            "username": "messager",
            "content": "Hello, world!",
            "message_type": "text"
        }
        
        response = client.post("/messages", json=message_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Message sent successfully"
        assert "message_id" in data

    def test_retrieve_room_messages(self, client):
        """Test retrieving messages from a room"""
        # Create room
        room_data = {"name": "History Test", "creator_id": 1}
        room_response = client.post("/rooms", json=room_data)
        room_id = room_response.json()["id"]
        
        # Send multiple messages
        messages_data = [
            {"room_id": room_id, "user_id": 1, "username": "user1", "content": "First message"},
            {"room_id": room_id, "user_id": 2, "username": "user2", "content": "Second message"},
            {"room_id": room_id, "user_id": 1, "username": "user1", "content": "Third message"}
        ]
        
        for msg_data in messages_data:
            client.post("/messages", json=msg_data)
        
        # Retrieve messages
        response = client.get(f"/rooms/{room_id}/messages")
        assert response.status_code == 200
        
        messages = response.json()
        assert len(messages) >= 3
        
        # Messages should be in chronological order (oldest first)
        assert messages[0]["content"] == "First message"
        assert messages[1]["content"] == "Second message"
        assert messages[2]["content"] == "Third message"

    def test_message_validation(self, client):
        """Test message validation"""
        # Test empty content
        invalid_message = {
            "room_id": "test-room",
            "user_id": 1,
            "username": "tester",
            "content": ""  # Empty content
        }
        
        response = client.post("/messages", json=invalid_message)
        assert response.status_code == 400
        
        # Test missing required fields
        incomplete_message = {
            "room_id": "test-room",
            "content": "Some content"
            # Missing user_id and username
        }
        
        response = client.post("/messages", json=incomplete_message)
        assert response.status_code == 400

class TestTypingIndicators:
    """Test typing indicator functionality"""
    
    @pytest.mark.asyncio
    async def test_typing_start_and_stop(self, client):
        """Test typing indicators via WebSocket"""
        with client.websocket_connect("/ws/test-room") as websocket:
            # Join room
            websocket.send_text(json.dumps({
                "type": "join",
                "user_id": 1,
                "username": "typer"
            }))
            websocket.receive_text()
            
            # Start typing
            websocket.send_text(json.dumps({
                "type": "typing_start",
                "user_id": 1,
                "username": "typer"
            }))
            
            # Stop typing
            websocket.send_text(json.dumps({
                "type": "typing_stop", 
                "user_id": 1,
                "username": "typer"
            }))

class TestMessageReplies:
    """Test message reply/threading functionality"""
    
    def test_reply_to_message(self, client):
        """Test replying to existing messages"""
        # Create room and send original message
        room_data = {"name": "Reply Test", "creator_id": 1}
        room_response = client.post("/rooms", json=room_data)
        room_id = room_response.json()["id"]
        
        # Send original message
        original_msg = {
            "room_id": room_id,
            "user_id": 1,
            "username": "original_poster",
            "content": "Original message"
        }
        original_response = client.post("/messages", json=original_msg)
        original_message_id = original_response.json()["message_id"]
        
        # Reply to the message
        reply_msg = {
            "room_id": room_id,
            "user_id": 2,
            "username": "replier",
            "content": "This is a reply",
            "message_type": "text",
            "parent_id": original_message_id
        }
        
        reply_response = client.post("/messages", json=reply_msg)
        assert reply_response.status_code == 200
        
        # Verify reply relationship is maintained
        messages_response = client.get(f"/rooms/{room_id}/messages")
        room_messages = messages_response.json()
        
        reply_message = next((msg for msg in room_messages if msg.get("parent_id") == original_message_id), None)
        assert reply_message is not None
        assert reply_message["content"] == "This is a reply"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])