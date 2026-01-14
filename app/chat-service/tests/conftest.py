"""Test configuration and fixtures"""

import pytest
from fastapi.testclient import TestClient
from chat_app.app import app
from chat_app.services import ChatService
from chat_app.models import CreateRoomRequest, JoinRoomRequest, MessageRequest

# Create a shared service instance for tests
chat_service = ChatService()

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
def sample_room_request():
    """Sample room creation request"""
    return CreateRoomRequest(
        name="Test Room",
        creator_id=1,
        description="A test room for unit testing",
        is_private=False
    )

@pytest.fixture
def sample_join_request():
    """Sample join room request"""
    return JoinRoomRequest(
        user_id=1,
        username="test_user"
    )

@pytest.fixture
def sample_message_request():
    """Sample message request"""
    return MessageRequest(
        room_id="test-room-id",
        user_id=1,
        username="test_user",
        content="Hello, world!",
        message_type="text"
    )

@pytest.fixture(autouse=True)
def clear_chat_service():
    """Clear chat service data before each test"""
    # Clear all data structures
    chat_service.chat_rooms.clear()
    chat_service.messages.clear()
    chat_service.user_presence.clear()
    chat_service.typing_users.clear()