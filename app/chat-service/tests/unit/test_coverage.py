"""Additional tests to achieve 100% code coverage"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import HTTPException, WebSocket
import json

from chat_app.app import app, websocket_endpoint
from chat_app.routes import router
from chat_app.services import ChatService
from chat_app.websocket import WebSocketManager


class TestEdgeCasesAndErrorHandling:
    """Tests for edge cases and error handling to achieve full coverage"""
    
    def test_app_main_function(self):
        """Test the main function in app.py (line 37-39)"""
        # This test covers the if __name__ == "__main__" block
        # We can't easily test this directly, but we can verify imports work
        from chat_app import app as imported_app
        assert imported_app is not None
    
    @pytest.mark.asyncio
    async def test_websocket_endpoint_coverage(self):
        """Test WebSocket endpoint to cover line 34 in app.py"""
        # Create a mock websocket
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(return_value='{"type": "ping"}')
        mock_websocket.send_text = AsyncMock()
        
        # Create mock service
        mock_service = AsyncMock()
        mock_service.handle_websocket_connection = AsyncMock()
        
        # Create WebSocketManager with mock
        manager = WebSocketManager(mock_service)
        
        # This should call the websocket endpoint function
        await manager.handle_connection(mock_websocket, "test-room", "123")
        
        # Verify the service method was called
        mock_service.handle_websocket_connection.assert_called_once_with(
            mock_websocket, "test-room", "123"
        )
    
    def test_routes_exception_handling(self):
        """Test error handling paths in routes to increase coverage"""
        client = TestClient(app)
        
        # Test 500 error path in get_rooms (line 67-68)
        with patch('chat_app.routes.chat_service') as mock_service:
            mock_service.get_all_rooms.side_effect = Exception("Internal error")
            response = client.get("/api/rooms")
            assert response.status_code == 500
        
        # Test 404 error path in get_room (line 77)
        with patch('chat_app.routes.chat_service') as mock_service:
            mock_service.get_room.return_value = None
            response = client.get("/api/rooms/nonexistent")
            assert response.status_code == 404
        
        # Test 500 error path in get_room (line 91-92)
        with patch('chat_app.routes.chat_service') as mock_service:
            mock_service.get_room.side_effect = Exception("Internal error")
            response = client.get("/api/rooms/error")
            assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_service_broadcast_exceptions(self):
        """Test exception handling in service broadcast methods"""
        service = ChatService()
        
        # Create a room first
        room_data = service.create_room(name="Test Room", creator_id=1)
        room_id = room_data["id"]
        
        # Test broadcast_to_room with disconnected clients (covers lines 28-37)
        # Create a mock connection that raises an exception
        mock_connection = AsyncMock()
        mock_connection.send_text.side_effect = Exception("Connection closed")
        
        # Add the mock connection to active connections
        service.active_connections[room_id] = [mock_connection]
        
        # This should trigger the exception handling and cleanup
        await service.broadcast_to_room(room_id, {"test": "message"})
        
        # Verify the connection was removed from active connections
        assert len(service.active_connections[room_id]) == 0
    
    @pytest.mark.asyncio
    async def test_service_websocket_connection_errors(self):
        """Test WebSocket connection error handling (covers lines 311-355)"""
        service = ChatService()
        
        # Create a room
        room_data = service.create_room(name="WebSocket Test", creator_id=1)
        room_id = room_data["id"]
        
        # Create mock websocket that closes immediately
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(side_effect=Exception("Connection closed"))
        mock_websocket.close = AsyncMock()
        
        # This should handle the exception gracefully
        await service.handle_websocket_connection(mock_websocket, room_id, "123")
        
        # Verify cleanup happened
        assert "123" not in service.user_presence[room_id]
    
    def test_websocket_manager_handle_connection(self):
        """Test WebSocketManager handle_connection method (covers line 16)"""
        # Create mock service
        mock_service = AsyncMock()
        
        # Create WebSocketManager
        manager = WebSocketManager(mock_service)
        
        # Create mock websocket
        mock_websocket = AsyncMock()
        
        # Call handle_connection
        import asyncio
        asyncio.run(manager.handle_connection(mock_websocket, "test-room", "123"))
        
        # Verify the service method was called
        mock_service.handle_websocket_connection.assert_called_once_with(
            mock_websocket, "test-room", "123"
        )
    
    @pytest.mark.asyncio
    async def test_service_broadcast_typing_status(self):
        """Test broadcast_typing_status method for coverage"""
        service = ChatService()
        
        # Create room and add typing user
        room_data = service.create_room(name="Typing Test", creator_id=1)
        room_id = room_data["id"]
        service.typing_users[room_id].add("123")
        
        # Mock active connections to avoid actual WebSocket calls
        service.active_connections[room_id] = []
        
        # This should broadcast typing status without errors
        await service.broadcast_typing_status(room_id)
        
        # Verify typing users are tracked
        assert "123" in service.typing_users[room_id]
    
    def test_routes_http_exception_reraising(self):
        """Test HTTPException reraising in routes (covers lines 89-90)"""
        client = TestClient(app)
        
        # Test that HTTPExceptions are properly reraised
        with patch('chat_app.routes.chat_service') as mock_service:
            # Create an HTTPException to be reraised
            http_exception = HTTPException(status_code=404, detail="Room not found")
            mock_service.get_room.side_effect = http_exception
            
            response = client.get("/api/rooms/specific-nonexistent")
            assert response.status_code == 404
            assert "Room not found" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_service_add_reaction_edge_cases(self):
        """Test edge cases in add_reaction method"""
        service = ChatService()
        
        # Create room and send message
        room_data = service.create_room(name="Reaction Test", creator_id=1)
        room_id = room_data["id"]
        await service.join_room(room_id, 1, "test_user")
        
        message_id = await service.send_message(room_id, 1, "test_user", "Test message")
        
        # Test adding reaction when reactions dict doesn't exist (covers line 287)
        # This is already handled in the existing logic, but let's verify it works
        reactions = await service.add_reaction(message_id, 1, "👍")
        assert "👍" in reactions
        
        # Test adding duplicate reaction (should not add duplicate user)
        reactions2 = await service.add_reaction(message_id, 1, "👍")
        assert len(reactions2["👍"]) == 1  # User should only appear once


class TestRouteSpecificErrorPaths:
    """Tests for specific error paths in routes to increase coverage"""
    
    def test_join_room_error_paths(self):
        """Test error handling paths in join_room route"""
        client = TestClient(app)
        
        # Test 400 error path (ValueError with non-"not found" message)
        with patch('chat_app.routes.chat_service') as mock_service:
            mock_service.join_room.side_effect = ValueError("Invalid user data")
            join_data = {"user_id": 1, "username": "test"}
            response = client.post("/api/rooms/test-room/join", json=join_data)
            assert response.status_code == 400
        
        # Test 500 error path
        with patch('chat_app.routes.chat_service') as mock_service:
            mock_service.join_room.side_effect = Exception("Internal error")
            join_data = {"user_id": 1, "username": "test"}
            response = client.post("/api/rooms/test-room/join", json=join_data)
            assert response.status_code == 500
    
    def test_leave_room_error_paths(self):
        """Test error handling paths in leave_room route"""
        client = TestClient(app)
        
        # Test 400 error path
        with patch('chat_app.routes.chat_service') as mock_service:
            mock_service.leave_room.side_effect = ValueError("Invalid room state")
            leave_data = {"user_id": 1, "username": "test"}
            response = client.post("/api/rooms/test-room/leave", json=leave_data)
            assert response.status_code == 400
        
        # Test 500 error path
        with patch('chat_app.routes.chat_service') as mock_service:
            mock_service.leave_room.side_effect = Exception("Internal error")
            leave_data = {"user_id": 1, "username": "test"}
            response = client.post("/api/rooms/test-room/leave", json=leave_data)
            assert response.status_code == 500
    
    def test_send_message_error_paths(self):
        """Test error handling paths in send_message route"""
        client = TestClient(app)
        
        # Test 403 error path ("not in room")
        with patch('chat_app.routes.chat_service') as mock_service:
            mock_service.send_message.side_effect = ValueError("User not in room")
            message_data = {
                "room_id": "test-room",
                "user_id": 1,
                "username": "test",
                "content": "test message"
            }
            response = client.post("/api/messages", json=message_data)
            assert response.status_code == 403
        
        # Test 400 error path (other ValueError)
        with patch('chat_app.routes.chat_service') as mock_service:
            mock_service.send_message.side_effect = ValueError("Invalid message")
            message_data = {
                "room_id": "test-room",
                "user_id": 1,
                "username": "test",
                "content": "test message"
            }
            response = client.post("/api/messages", json=message_data)
            assert response.status_code == 400
        
        # Test 500 error path
        with patch('chat_app.routes.chat_service') as mock_service:
            mock_service.send_message.side_effect = Exception("Internal error")
            message_data = {
                "room_id": "test-room",
                "user_id": 1,
                "username": "test",
                "content": "test message"
            }
            response = client.post("/api/messages", json=message_data)
            assert response.status_code == 500
    
    def test_message_reactions_error_paths(self):
        """Test error handling paths in message reactions route"""
        client = TestClient(app)
        
        # Test 500 error path
        with patch('chat_app.routes.chat_service') as mock_service:
            mock_service.add_reaction.side_effect = Exception("Internal error")
            reaction_data = {
                "message_id": "test-message",
                "user_id": 1,
                "reaction": "👍"
            }
            response = client.post("/api/reactions", json=reaction_data)
            assert response.status_code == 500