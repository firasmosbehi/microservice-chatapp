"""
Test configuration and fixtures for Chat Service
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
from main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket connection"""
    websocket = AsyncMock()
    websocket.accept = AsyncMock()
    websocket.send_text = AsyncMock()
    websocket.receive_text = AsyncMock()
    websocket.close = AsyncMock()
    return websocket

@pytest.fixture
def sample_room_data():
    """Sample room creation data"""
    return {
        "name": "Test Room",
        "creator_id": 1,
        "description": "A test room for unit testing",
        "is_private": False
    }

@pytest.fixture
def sample_user_data():
    """Sample user data for joining rooms"""
    return {
        "user_id": 1,
        "username": "testuser"
    }

@pytest.fixture
def sample_message_data():
    """Sample message data"""
    return {
        "room_id": "test-room-123",
        "user_id": 1,
        "username": "sender",
        "content": "Hello, this is a test message!",
        "message_type": "text"
    }

@pytest.fixture(autouse=True)
def cleanup_global_state():
    """Automatically clean up global state before each test"""
    from main import chat_rooms, messages, active_connections, user_sessions, user_presence, typing_users
    
    # Clear all global dictionaries
    chat_rooms.clear()
    messages.clear()
    active_connections.clear()
    user_sessions.clear()
    user_presence.clear()
    typing_users.clear()
    
    yield  # Allow test to run
    
    # Clean up after test
    chat_rooms.clear()
    messages.clear()
    active_connections.clear()
    user_sessions.clear()
    user_presence.clear()
    typing_users.clear()

# Custom markers for test categorization
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "websocket: mark test as testing WebSocket functionality"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )

# Test utilities
class WebSocketTester:
    """Helper class for WebSocket testing"""
    
    def __init__(self, client):
        self.client = client
        self.connections = []
    
    def connect(self, room_id):
        """Establish WebSocket connection to a room"""
        websocket = self.client.websocket_connect(f"/ws/{room_id}")
        self.connections.append(websocket)
        return websocket
    
    def disconnect_all(self):
        """Close all WebSocket connections"""
        for conn in self.connections:
            try:
                conn.close()
            except:
                pass
        self.connections.clear()

@pytest.fixture
def ws_tester(client):
    """Create WebSocket tester instance"""
    tester = WebSocketTester(client)
    yield tester
    tester.disconnect_all()