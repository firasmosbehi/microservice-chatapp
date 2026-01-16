"""Final test to achieve 100% code coverage"""

import pytest
from unittest.mock import AsyncMock
from fastapi import WebSocket
import json

from chat_app.services import ChatService


class TestAbsoluteFinalCoverage:
    """Final tests to hit the last remaining uncovered lines"""
    
    @pytest.mark.asyncio
    async def test_json_decode_error_coverage(self):
        """Test line 345 - JSON decode error handling"""
        service = ChatService()
        
        # Create room and join
        room_data = service.create_room(name="JSON Error Test", creator_id=1)
        room_id = room_data["id"]
        await service.join_room(room_id, 1, "test_user")
        
        # Create mock websocket that sends invalid JSON
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(return_value='{"invalid": json}')  # Invalid JSON
        mock_websocket.send_text = AsyncMock()
        
        # Mock active connections
        service.active_connections[room_id] = [mock_websocket]
        
        # This should trigger the JSONDecodeError and hit line 345
        await service.handle_websocket_connection(mock_websocket, room_id, "1")
        
        # Verify the error response was sent
        mock_websocket.send_text.assert_called_with("Invalid JSON format")
    
    @pytest.mark.asyncio 
    async def test_typing_status_update_coverage(self):
        """Test line 335 - typing status update in WebSocket handler"""
        service = ChatService()
        
        # Create room and join
        room_data = service.create_room(name="Typing WebSocket Test", creator_id=1)
        room_id = room_data["id"]
        await service.join_room(room_id, 1, "test_user")
        
        # Create mock websocket that sends typing message
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(return_value='{"type": "typing", "is_typing": true}')
        mock_websocket.send_text = AsyncMock()
        
        # Mock the update_typing_status method to verify it's called
        original_method = service.update_typing_status
        service.update_typing_status = AsyncMock()
        
        # Mock active connections
        service.active_connections[room_id] = [mock_websocket]
        
        # This should trigger the typing branch and call update_typing_status (line 335)
        await service.handle_websocket_connection(mock_websocket, room_id, "1")
        
        # Verify update_typing_status was called
        service.update_typing_status.assert_called_once_with(
            room_id=room_id,
            user_id=1,
            is_typing=True
        )
        
        # Restore original method
        service.update_typing_status = original_method