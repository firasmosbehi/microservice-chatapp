"""Tests for Pydantic models"""

import pytest
from datetime import datetime
from chat_app.models import (
    CreateRoomRequest, JoinRoomRequest, MessageRequest,
    TypingRequest, MessageReaction, RoomResponse
)


class TestCreateRoomRequest:
    """Tests for CreateRoomRequest model"""
    
    def test_create_room_request_valid(self):
        """Test creating valid room request"""
        request = CreateRoomRequest(
            name="Test Room",
            creator_id=1,
            description="A test room",
            is_private=False,
            invited_users=[2, 3]
        )
        
        assert request.name == "Test Room"
        assert request.creator_id == 1
        assert request.description == "A test room"
        assert request.is_private is False
        assert request.invited_users == [2, 3]
    
    def test_create_room_request_defaults(self):
        """Test room request with default values"""
        request = CreateRoomRequest(
            name="Test Room",
            creator_id=1
        )
        
        assert request.description is None
        assert request.is_private is False
        assert request.invited_users is None


class TestJoinRoomRequest:
    """Tests for JoinRoomRequest model"""
    
    def test_join_room_request_valid(self):
        """Test creating valid join request"""
        request = JoinRoomRequest(
            user_id=1,
            username="test_user"
        )
        
        assert request.user_id == 1
        assert request.username == "test_user"


class TestMessageRequest:
    """Tests for MessageRequest model"""
    
    def test_message_request_valid(self):
        """Test creating valid message request"""
        request = MessageRequest(
            room_id="room-123",
            user_id=1,
            username="test_user",
            content="Hello world!",
            message_type="text",
            parent_id="msg-456"
        )
        
        assert request.room_id == "room-123"
        assert request.user_id == 1
        assert request.username == "test_user"
        assert request.content == "Hello world!"
        assert request.message_type == "text"
        assert request.parent_id == "msg-456"
    
    def test_message_request_default_type(self):
        """Test message request with default type"""
        request = MessageRequest(
            room_id="room-123",
            user_id=1,
            username="test_user",
            content="Hello"
        )
        
        assert request.message_type == "text"
        assert request.parent_id is None


class TestRoomResponse:
    """Tests for RoomResponse model"""
    
    def test_room_response_valid(self):
        """Test creating valid room response"""
        response = RoomResponse(
            id="room-123",
            name="Test Room",
            description="A test room",
            creator_id=1,
            created_at=datetime.now().isoformat(),
            member_count=5,
            is_private=False,
            online_members=3
        )
        
        assert response.id == "room-123"
        assert response.name == "Test Room"
        assert response.member_count == 5
        assert response.online_members == 3


class TestTypingRequest:
    """Tests for TypingRequest model"""
    
    def test_typing_request_valid(self):
        """Test creating valid typing request"""
        request = TypingRequest(
            room_id="room-123",
            user_id=1,
            username="test_user",
            is_typing=True
        )
        
        assert request.room_id == "room-123"
        assert request.user_id == 1
        assert request.username == "test_user"
        assert request.is_typing is True


class TestMessageReaction:
    """Tests for MessageReaction model"""
    
    def test_message_reaction_valid(self):
        """Test creating valid message reaction"""
        reaction = MessageReaction(
            message_id="msg-123",
            user_id=1,
            reaction="👍"
        )
        
        assert reaction.message_id == "msg-123"
        assert reaction.user_id == 1
        assert reaction.reaction == "👍"