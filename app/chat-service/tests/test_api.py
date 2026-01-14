"""Tests for API endpoints"""

import pytest
from fastapi.testclient import TestClient
from chat_app.app import app
from chat_app.models import CreateRoomRequest, JoinRoomRequest, MessageRequest

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert data["message"] == "Advanced Chat Service Running"
        assert "version" in data
        assert "features" in data


class TestRoomEndpoints:
    """Tests for room management endpoints"""
    
    def test_create_room(self):
        """Test creating a new room"""
        room_data = {
            "name": "Test Room",
            "creator_id": 1,
            "description": "A test room",
            "is_private": False
        }
        
        response = client.post("/api/rooms", json=room_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["name"] == "Test Room"
        assert data["creator_id"] == 1
        assert data["member_count"] == 1
    
    def test_get_rooms(self):
        """Test getting all rooms"""
        response = client.get("/api/rooms")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_specific_room(self):
        """Test getting a specific room"""
        # First create a room
        room_data = {
            "name": "Test Room",
            "creator_id": 1
        }
        create_response = client.post("/api/rooms", json=room_data)
        room_id = create_response.json()["id"]
        
        # Then get the room
        response = client.get(f"/api/rooms/{room_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == room_id
        assert data["name"] == "Test Room"


class TestMessageEndpoints:
    """Tests for message endpoints"""
    
    def test_send_message_room_not_found(self):
        """Test sending message to non-existent room"""
        message_data = {
            "room_id": "non-existent-room",
            "user_id": 1,
            "username": "test_user",
            "content": "Hello world!"
        }
        
        response = client.post("/api/messages", json=message_data)
        assert response.status_code == 404


class TestTypingEndpoint:
    """Tests for typing indicator endpoint"""
    
    def test_update_typing_status_room_not_found(self):
        """Test updating typing status for non-existent room"""
        typing_data = {
            "room_id": "non-existent-room",
            "user_id": 1,
            "username": "test_user",
            "is_typing": True
        }
        
        response = client.post("/api/typing", json=typing_data)
        assert response.status_code == 404


class TestReactionsEndpoint:
    """Tests for message reactions endpoint"""
    
    def test_add_reaction_message_not_found(self):
        """Test adding reaction to non-existent message"""
        reaction_data = {
            "message_id": "non-existent-message",
            "user_id": 1,
            "reaction": "👍"
        }
        
        response = client.post("/api/reactions", json=reaction_data)
        assert response.status_code == 404