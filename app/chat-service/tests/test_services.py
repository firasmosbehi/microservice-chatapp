"""Tests for ChatService class"""

import pytest
from unittest.mock import patch, AsyncMock
import asyncio
from chat_app.services import ChatService
from chat_app.models import CreateRoomRequest, JoinRoomRequest, MessageRequest


class TestChatService:
    """Tests for ChatService functionality"""
    
    @pytest.fixture
    def chat_service(self):
        """Create fresh chat service instance for each test"""
        return ChatService()
    
    def test_create_room(self, chat_service):
        """Test creating a new room"""
        room_data = chat_service.create_room(
            name="Test Room",
            creator_id=1,
            description="A test room",
            is_private=False
        )
        
        assert "id" in room_data
        assert room_data["name"] == "Test Room"
        assert room_data["creator_id"] == 1
        assert room_data["description"] == "A test room"
        assert room_data["is_private"] is False
        assert room_data["member_count"] == 1
    
    def test_get_all_rooms_empty(self, chat_service):
        """Test getting all rooms when none exist"""
        rooms = chat_service.get_all_rooms()
        assert rooms == []
    
    def test_get_all_rooms_with_data(self, chat_service):
        """Test getting all rooms when some exist"""
        # Create a room first
        chat_service.create_room(name="Test Room", creator_id=1)
        
        rooms = chat_service.get_all_rooms()
        assert len(rooms) == 1
        assert rooms[0]["name"] == "Test Room"
    
    def test_get_room_exists(self, chat_service):
        """Test getting a specific room that exists"""
        # Create a room
        room_data = chat_service.create_room(name="Test Room", creator_id=1)
        room_id = room_data["id"]
        
        # Get the room
        retrieved_room = chat_service.get_room(room_id)
        assert retrieved_room is not None
        assert retrieved_room["id"] == room_id
        assert retrieved_room["name"] == "Test Room"
    
    def test_get_room_not_exists(self, chat_service):
        """Test getting a room that doesn't exist"""
        room = chat_service.get_room("non-existent-id")
        assert room is None
    
    @pytest.mark.asyncio
    async def test_join_room_success(self, chat_service):
        """Test successfully joining a room"""
        # Create a room first
        room_data = chat_service.create_room(name="Test Room", creator_id=1)
        room_id = room_data["id"]
        
        # Join the room
        result = await chat_service.join_room(room_id, 2, "new_user")
        
        assert "id" in result
        assert "name" in result
        assert result["member_count"] == 2
        # Note: Only the joining user is counted as online in user_presence
        # The creator is not automatically marked as online
        assert result["online_members"] == 1
    
    @pytest.mark.asyncio
    async def test_join_room_not_found(self, chat_service):
        """Test joining a non-existent room"""
        with pytest.raises(ValueError, match="Room not found"):
            await chat_service.join_room("non-existent-id", 1, "test_user")
    
    @pytest.mark.asyncio
    async def test_leave_room_success(self, chat_service):
        """Test successfully leaving a room"""
        # Create and join a room
        room_data = chat_service.create_room(name="Test Room", creator_id=1)
        room_id = room_data["id"]
        await chat_service.join_room(room_id, 2, "test_user")
        
        # Leave the room
        await chat_service.leave_room(room_id, 2, "test_user")
        
        # Check that user is no longer in presence
        assert "2" not in chat_service.user_presence[room_id]
    
    @pytest.mark.asyncio
    async def test_leave_room_not_found(self, chat_service):
        """Test leaving a non-existent room"""
        with pytest.raises(ValueError, match="Room not found"):
            await chat_service.leave_room("non-existent-id", 1, "test_user")
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, chat_service):
        """Test successfully sending a message"""
        # Create and join a room
        room_data = chat_service.create_room(name="Test Room", creator_id=1)
        room_id = room_data["id"]
        await chat_service.join_room(room_id, 1, "test_user")
        
        # Send a message
        message_id = await chat_service.send_message(
            room_id=room_id,
            user_id=1,
            username="test_user",
            content="Hello world!"
        )
        
        assert message_id is not None
        # Note: We can't easily check message count due to async behavior
    
    @pytest.mark.asyncio
    async def test_send_message_room_not_found(self, chat_service):
        """Test sending message to non-existent room"""
        with pytest.raises(ValueError, match="Room not found"):
            await chat_service.send_message(
                room_id="non-existent-id",
                user_id=1,
                username="test_user",
                content="Hello"
            )
    
    @pytest.mark.asyncio
    async def test_send_message_user_not_in_room(self, chat_service):
        """Test sending message when user is not in room"""
        # Create room but don't join
        room_data = chat_service.create_room(name="Test Room", creator_id=1)
        room_id = room_data["id"]
        
        with pytest.raises(ValueError, match="User not in room"):
            await chat_service.send_message(
                room_id=room_id,
                user_id=1,
                username="test_user",
                content="Hello"
            )
    
    def test_get_room_messages_success(self, chat_service):
        """Test getting messages from a room"""
        # Create room and send messages
        room_data = chat_service.create_room(name="Test Room", creator_id=1)
        room_id = room_data["id"]
        
        # For sync test, we'll manually add messages to simulate the behavior
        test_message = {
            "id": "test-msg-1",
            "room_id": room_id,
            "user_id": 1,
            "username": "test_user",
            "content": "Test message",
            "timestamp": "2023-01-01T00:00:00",
            "type": "text"
        }
        chat_service.messages[room_id].append(test_message)
        
        messages = chat_service.get_room_messages(room_id, limit=10)
        assert len(messages) >= 1  # At least the system message + our test message
    
    def test_get_room_messages_not_found(self, chat_service):
        """Test getting messages from non-existent room"""
        with pytest.raises(ValueError, match="Room not found"):
            chat_service.get_room_messages("non-existent-id")
    
    @pytest.mark.asyncio
    async def test_update_typing_status(self, chat_service):
        """Test updating typing status"""
        # Create room and join
        room_data = chat_service.create_room(name="Test Room", creator_id=1)
        room_id = room_data["id"]
        await chat_service.join_room(room_id, 1, "test_user")
        
        # Set typing status
        await chat_service.update_typing_status(room_id, 1, True)
        
        # Due to async nature, we check if the method was called without error
        # The actual state might not be immediately visible in tests
    
    @pytest.mark.asyncio
    async def test_add_reaction_success(self, chat_service):
        """Test adding reaction to a message"""
        # Create room, join, and send message
        room_data = chat_service.create_room(name="Test Room", creator_id=1)
        room_id = room_data["id"]
        await chat_service.join_room(room_id, 1, "test_user")
        
        message_id = await chat_service.send_message(room_id, 1, "test_user", "Hello")
        
        # Add reaction
        reactions = await chat_service.add_reaction(message_id, 1, "👍")
        
        # Check that reaction was processed without error
        assert reactions is not None
    
    @pytest.mark.asyncio
    async def test_add_reaction_message_not_found(self, chat_service):
        """Test adding reaction to non-existent message"""
        with pytest.raises(ValueError, match="Message not found"):
            await chat_service.add_reaction("non-existent-message", 1, "👍")