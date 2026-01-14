"""WebSocket handlers for real-time chat functionality"""

from fastapi import WebSocket, WebSocketDisconnect
import json

from .services import ChatService


class WebSocketManager:
    """Manages WebSocket connections and real-time communication"""
    
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service
    
    async def handle_connection(self, websocket: WebSocket, room_id: str, user_id: str):
        """Handle WebSocket connection lifecycle"""
        await self.chat_service.handle_websocket_connection(websocket, room_id, user_id)