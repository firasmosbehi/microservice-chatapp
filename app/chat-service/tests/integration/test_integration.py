"""Integration tests for the chat service to verify components work together"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import asyncio
from chat_app.app import app
from chat_app.services import ChatService
from chat_app.models import CreateRoomRequest, JoinRoomRequest, MessageRequest


class TestChatIntegration:
    """Integration tests for chat service components"""
    
    def test_full_room_lifecycle_integration(self):
        """Test complete room lifecycle: create → join → message → leave"""
        client = TestClient(app)
        
        # Step 1: Create a room
        room_data = {
            "name": "Integration Test Room",
            "creator_id": 1,
            "description": "A room for integration testing"
        }
        
        response = client.post("/api/rooms", json=room_data)
        assert response.status_code == 200
        created_room = response.json()
        assert "id" in created_room
        assert created_room["name"] == "Integration Test Room"
        room_id = created_room["id"]
        
        # Step 2: Join the room
        join_data = {
            "user_id": 2,
            "username": "test_user_2"
        }
        
        join_response = client.post(f"/api/rooms/{room_id}/join", json=join_data)
        assert join_response.status_code == 200
        assert "Successfully joined room" in join_response.json()["message"]
        
        # Step 3: Send a message
        message_data = {
            "room_id": room_id,
            "user_id": 2,
            "username": "test_user_2",
            "content": "Hello from integration test!"
        }
        
        message_response = client.post("/api/messages", json=message_data)
        assert message_response.status_code == 200
        message_result = message_response.json()
        assert "Message sent successfully" in message_result["message"]
        assert "message_id" in message_result
        
        # Step 4: Get room messages
        messages_response = client.get(f"/api/rooms/{room_id}/messages")
        assert messages_response.status_code == 200
        messages = messages_response.json()
        assert len(messages) >= 1  # At least the system message + our test message
        # Verify our message is in the response
        message_found = any(msg["content"] == "Hello from integration test!" for msg in messages)
        assert message_found, "Test message should be found in room messages"
        
        # Step 5: Leave the room
        leave_data = {
            "user_id": 2,
            "username": "test_user_2"
        }
        
        leave_response = client.post(f"/api/rooms/{room_id}/leave", json=leave_data)
        assert leave_response.status_code == 200
        assert "Successfully left room" in leave_response.json()["message"]
    
    def test_multiple_users_interaction(self):
        """Test interaction between multiple users in a room"""
        client = TestClient(app)
        
        # Create a room
        room_data = {
            "name": "Multi-user Test Room",
            "creator_id": 1,
            "description": "A room for multi-user testing"
        }
        
        response = client.post("/api/rooms", json=room_data)
        assert response.status_code == 200
        room_id = response.json()["id"]
        
        # First user joins
        join_data_1 = {"user_id": 1, "username": "user_1"}
        client.post(f"/api/rooms/{room_id}/join", json=join_data_1)
        
        # Second user joins
        join_data_2 = {"user_id": 2, "username": "user_2"}
        join_response = client.post(f"/api/rooms/{room_id}/join", json=join_data_2)
        assert join_response.status_code == 200
        
        # Get all rooms to verify room exists
        rooms_response = client.get("/api/rooms")
        assert rooms_response.status_code == 200
        rooms = rooms_response.json()
        room_found = any(room["id"] == room_id for room in rooms)
        assert room_found, "Created room should appear in room list"
    
    def test_typing_indicator_integration(self):
        """Test typing indicator functionality integration"""
        client = TestClient(app)
        
        # Create a room
        room_data = {
            "name": "Typing Test Room",
            "creator_id": 1
        }
        
        response = client.post("/api/rooms", json=room_data)
        assert response.status_code == 200
        room_id = response.json()["id"]
        
        # Join the room
        join_data = {"user_id": 1, "username": "typist"}
        client.post(f"/api/rooms/{room_id}/join", json=join_data)
        
        # Update typing status
        typing_data = {
            "room_id": room_id,
            "user_id": 1,
            "username": "typist",
            "is_typing": True
        }
        
        typing_response = client.post("/api/typing", json=typing_data)
        assert typing_response.status_code == 200
        assert "Typing status updated" in typing_response.json()["message"]
    
    def test_message_reaction_integration(self):
        """Test message reaction functionality integration"""
        client = TestClient(app)
        
        # Create a room
        room_data = {
            "name": "Reaction Test Room",
            "creator_id": 1
        }
        
        response = client.post("/api/rooms", json=room_data)
        assert response.status_code == 200
        room_id = response.json()["id"]
        
        # Join the room
        join_data = {"user_id": 1, "username": "reactor"}
        client.post(f"/api/rooms/{room_id}/join", json=join_data)
        
        # Send a message first
        message_data = {
            "room_id": room_id,
            "user_id": 1,
            "username": "reactor",
            "content": "Message to react to"
        }
        
        message_response = client.post("/api/messages", json=message_data)
        assert message_response.status_code == 200
        message_id = message_response.json()["message_id"]
        
        # Add a reaction to the message
        reaction_data = {
            "message_id": message_id,
            "user_id": 1,
            "reaction": "👍"
        }
        
        reaction_response = client.post("/api/reactions", json=reaction_data)
        assert reaction_response.status_code == 200
        assert "Reaction added successfully" in reaction_response.json()["message"]
    
    def test_error_handling_integration(self):
        """Test error handling across multiple components"""
        client = TestClient(app)
        
        # Try to send message to non-existent room
        message_data = {
            "room_id": "invalid-room-id",
            "user_id": 1,
            "username": "test_user",
            "content": "This should fail"
        }
        
        response = client.post("/api/messages", json=message_data)
        assert response.status_code == 404
        
        # Try to join non-existent room
        join_data = {"user_id": 1, "username": "test_user"}
        join_response = client.post("/api/rooms/invalid-room-id/join", json=join_data)
        assert join_response.status_code == 404
        
        # Try to update typing status for non-existent room
        typing_data = {
            "room_id": "invalid-room-id",
            "user_id": 1,
            "username": "test_user",
            "is_typing": True
        }
        
        typing_response = client.post("/api/typing", json=typing_data)
        assert typing_response.status_code == 404


class TestServiceIntegration:
    """Integration tests for service layer components"""
    
    def test_service_layer_composition(self):
        """Test that service methods work together correctly"""
        service = ChatService()
        
        # Create a room
        room_data = service.create_room(
            name="Service Integration Room",
            creator_id=1,
            description="Testing service composition"
        )
        
        assert "id" in room_data
        assert room_data["name"] == "Service Integration Room"
        room_id = room_data["id"]
        
        # Verify room exists
        retrieved_room = service.get_room(room_id)
        assert retrieved_room is not None
        assert retrieved_room["name"] == "Service Integration Room"
        
        # Get all rooms and verify our room is there
        all_rooms = service.get_all_rooms()
        assert len(all_rooms) == 1
        assert all_rooms[0]["id"] == room_id
        
        # Join the room
        join_result = asyncio.run(service.join_room(room_id, 2, "integration_tester"))
        assert "id" in join_result
        assert join_result["member_count"] == 2  # Creator + new member
    
    def test_message_flow_integration(self):
        """Test complete message flow through service layer"""
        service = ChatService()
        
        # Create room and join
        room_data = service.create_room(name="Message Flow Room", creator_id=1)
        room_id = room_data["id"]
        
        # Join room
        asyncio.run(service.join_room(room_id, 2, "sender"))
        
        # Send message
        message_id = asyncio.run(
            service.send_message(
                room_id=room_id,
                user_id=2,
                username="sender",
                content="Integration test message"
            )
        )
        
        assert message_id is not None
        
        # Get messages
        messages = service.get_room_messages(room_id)
        assert len(messages) >= 1  # System message + our message
        
        # Verify our message is present
        message_found = any(
            msg.get("content") == "Integration test message" 
            for msg in messages
        )
        assert message_found, "Test message should be in room messages"


class TestAPIAndServiceIntegration:
    """Tests that verify API endpoints properly interact with service layer"""
    
    @patch('chat_app.routes.chat_service')
    def test_api_calls_service_methods(self, mock_chat_service):
        """Test that API endpoints call appropriate service methods"""
        client = TestClient(app)
        
        # Mock service methods
        mock_chat_service.create_room.return_value = {
            "id": "test-room-id",
            "name": "Test Room",
            "description": "Test Description",
            "creator_id": 1,
            "created_at": "2023-01-01T00:00:00",
            "member_count": 1,
            "is_private": False,
            "online_members": 1
        }
        
        # Call API
        room_data = {
            "name": "Test Room",
            "creator_id": 1,
            "description": "Test Description"
        }
        
        response = client.post("/api/rooms", json=room_data)
        
        # Verify API responded correctly
        assert response.status_code == 200
        assert response.json()["name"] == "Test Room"
        
        # Verify service method was called
        mock_chat_service.create_room.assert_called_once()
    
    @patch('chat_app.routes.chat_service')
    def test_api_error_propagation(self, mock_chat_service):
        """Test that API properly propagates service errors"""
        client = TestClient(app)
        
        # Mock service to raise an exception
        mock_chat_service.create_room.side_effect = Exception("Service error")
        
        room_data = {
            "name": "Test Room",
            "creator_id": 1
        }
        
        response = client.post("/api/rooms", json=room_data)
        
        # Verify API returns error
        assert response.status_code == 500