"""Business logic services for chat service"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Set, Optional
from collections import defaultdict
import asyncio

from fastapi import WebSocket


class ChatService:
    """Main service class handling chat business logic"""

    def __init__(self) -> None:
        # Enhanced in-memory storage
        self.chat_rooms: Dict[str, Dict] = {}
        self.messages: Dict[str, List[Dict]] = defaultdict(list)
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.user_presence: Dict[str, Set[str]] = defaultdict(
            set
        )  # room_id -> set of user_ids
        self.typing_users: Dict[str, Set[str]] = defaultdict(
            set
        )  # room_id -> set of typing user_ids

    async def broadcast_to_room(self, room_id: str, message: dict) -> None:
        """Broadcast message to all connections in a room"""
        if room_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)

            # Clean up disconnected clients
            for conn in disconnected:
                self.active_connections[room_id].remove(conn)

    async def notify_user_presence(
        self, room_id: str, user_id: int, username: str, status: str
    ) -> None:
        """Notify room about user presence changes"""
        presence_message = {
            "type": "presence_change",
            "user_id": user_id,
            "username": username,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast_to_room(room_id, presence_message)

    def create_room(
        self,
        name: str,
        creator_id: int,
        description: Optional[str] = None,
        is_private: bool = False,
        invited_users: Optional[List[int]] = None,
    ) -> Dict:
        """Create a new chat room"""
        room_id = str(uuid.uuid4())

        # Get creator username (you might want to fetch this from user service)
        creator_username = f"User_{creator_id}"  # Placeholder

        room_data = {
            "id": room_id,
            "name": name,
            "description": description,
            "creator_id": creator_id,
            "created_at": datetime.now().isoformat(),
            "members": {creator_id: creator_username},
            "member_count": 1,
            "is_private": is_private,
            "invited_users": invited_users or [],
            "online_members": 1,
        }

        self.chat_rooms[room_id] = room_data
        self.messages[room_id] = []

        # Create system message
        system_msg = {
            "id": str(uuid.uuid4()),
            "room_id": room_id,
            "user_id": 0,
            "username": "System",
            "content": f"Room '{name}' created by User_{creator_id}",
            "timestamp": datetime.now().isoformat(),
            "type": "system",
        }

        self.messages[room_id].append(system_msg)

        return room_data

    def get_all_rooms(self) -> List[Dict]:
        """Get all chat rooms"""
        return [
            {
                "id": room["id"],
                "name": room["name"],
                "description": room["description"],
                "creator_id": room["creator_id"],
                "created_at": room["created_at"],
                "member_count": room["member_count"],
                "is_private": room["is_private"],
                "online_members": len(self.user_presence.get(room["id"], set())),
            }
            for room in self.chat_rooms.values()
        ]

    def get_room(self, room_id: str) -> Optional[Dict]:
        """Get specific room details"""
        return self.chat_rooms.get(room_id)

    async def join_room(self, room_id: str, user_id: int, username: str) -> Dict:
        """Join a chat room"""
        if room_id not in self.chat_rooms:
            raise ValueError("Room not found")

        # Add user to room members
        self.chat_rooms[room_id]["members"][user_id] = username
        self.chat_rooms[room_id]["member_count"] = len(
            self.chat_rooms[room_id]["members"]
        )

        # Track user presence
        self.user_presence[room_id].add(str(user_id))
        self.chat_rooms[room_id]["online_members"] = len(self.user_presence[room_id])

        # Create welcome message
        welcome_msg = {
            "id": str(uuid.uuid4()),
            "room_id": room_id,
            "user_id": user_id,
            "username": username,
            "content": f"{username} joined the room",
            "timestamp": datetime.now().isoformat(),
            "type": "system",
        }

        self.messages[room_id].append(welcome_msg)

        # Notify presence change
        await self.notify_user_presence(room_id, user_id, username, "joined")

        # Broadcast join event
        join_event = {
            "type": "user_joined",
            "user_id": user_id,
            "username": username,
            "room_id": room_id,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast_to_room(room_id, join_event)

        # Broadcast welcome message
        message_event = {"type": "message", "message": welcome_msg}
        await self.broadcast_to_room(room_id, message_event)

        return {
            "id": self.chat_rooms[room_id]["id"],
            "name": self.chat_rooms[room_id]["name"],
            "member_count": self.chat_rooms[room_id]["member_count"],
            "online_members": self.chat_rooms[room_id]["online_members"],
        }

    async def leave_room(self, room_id: str, user_id: int, username: str) -> None:
        """Leave a chat room"""
        if room_id not in self.chat_rooms:
            raise ValueError("Room not found")

        if str(user_id) in self.user_presence[room_id]:
            # Remove from presence tracking
            self.user_presence[room_id].discard(str(user_id))
            self.chat_rooms[room_id]["online_members"] = len(
                self.user_presence[room_id]
            )

            # Remove from typing indicators if typing
            self.typing_users[room_id].discard(str(user_id))

            # Create leave message
            leave_msg = {
                "id": str(uuid.uuid4()),
                "room_id": room_id,
                "user_id": user_id,
                "username": username,
                "content": f"{username} left the room",
                "timestamp": datetime.now().isoformat(),
                "type": "system",
            }

            self.messages[room_id].append(leave_msg)

            # Notify presence change
            await self.notify_user_presence(room_id, user_id, username, "left")

            # Broadcast leave event
            leave_event = {
                "type": "user_left",
                "user_id": user_id,
                "username": username,
                "room_id": room_id,
                "timestamp": datetime.now().isoformat(),
            }
            await self.broadcast_to_room(room_id, leave_event)

            # Broadcast leave message
            message_event = {"type": "message", "message": leave_msg}
            await self.broadcast_to_room(room_id, message_event)

    async def send_message(
        self,
        room_id: str,
        user_id: int,
        username: str,
        content: str,
        message_type: str = "text",
        parent_id: Optional[str] = None,
    ) -> str:
        """Send a message to a chat room"""
        if room_id not in self.chat_rooms:
            raise ValueError("Room not found")

        if str(user_id) not in self.user_presence[room_id]:
            raise ValueError("User not in room")

        # Create message
        message_id = str(uuid.uuid4())
        message = {
            "id": message_id,
            "room_id": room_id,
            "user_id": user_id,
            "username": username,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "type": message_type,
            "parent_id": parent_id,
            "reactions": {},
        }

        # Store message
        self.messages[room_id].append(message)

        # Broadcast message to room
        message_event = {"type": "message", "message": message}
        await self.broadcast_to_room(room_id, message_event)

        # Clear typing indicator for this user
        self.typing_users[room_id].discard(str(user_id))
        await self.broadcast_typing_status(room_id)

        return message_id

    def get_room_messages(
        self, room_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict]:
        """Get messages for a specific room"""
        if room_id not in self.chat_rooms:
            raise ValueError("Room not found")

        room_messages = self.messages[room_id]
        # Return messages in reverse chronological order (newest first)
        return room_messages[::-1][offset : offset + limit]

    async def update_typing_status(
        self, room_id: str, user_id: int, is_typing: bool
    ) -> None:
        """Update typing status for a user in a room"""
        if room_id not in self.chat_rooms:
            raise ValueError("Room not found")

        if is_typing:
            self.typing_users[room_id].add(str(user_id))
        else:
            self.typing_users[room_id].discard(str(user_id))

        await self.broadcast_typing_status(room_id)

    async def broadcast_typing_status(self, room_id: str) -> None:
        """Broadcast current typing users to the room"""
        typing_list = list(self.typing_users[room_id])
        typing_event = {
            "type": "typing_update",
            "room_id": room_id,
            "typing_users": typing_list,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast_to_room(room_id, typing_event)

    async def add_reaction(self, message_id: str, user_id: int, reaction: str) -> dict:
        """Add reaction to a message"""
        # Find the message and add reaction
        for room_id, room_messages in self.messages.items():
            for msg in room_messages:
                if msg["id"] == message_id:
                    if "reactions" not in msg:
                        msg["reactions"] = {}

                    if reaction not in msg["reactions"]:
                        msg["reactions"][reaction] = []

                    if user_id not in msg["reactions"][reaction]:
                        msg["reactions"][reaction].append(user_id)

                    # Broadcast reaction update
                    reaction_event = {
                        "type": "reaction_added",
                        "message_id": message_id,
                        "reaction": reaction,
                        "user_id": user_id,
                        "reactions": msg["reactions"],
                    }
                    await self.broadcast_to_room(room_id, reaction_event)
                    reactions: dict = msg["reactions"]
                    return reactions

        raise ValueError("Message not found")

    async def handle_websocket_connection(
        self, websocket: WebSocket, room_id: str, user_id: str
    ) -> None:
        """Handle WebSocket connection lifecycle"""
        if room_id not in self.chat_rooms:
            await websocket.close(code=4004, reason="Room not found")
            return

        await websocket.accept()

        # Add connection to room
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                try:
                    message_data = json.loads(data)

                    # Handle different message types
                    if message_data.get("type") == "ping":
                        # Heartbeat message
                        await websocket.send_text(json.dumps({"type": "pong"}))
                    elif message_data.get("type") == "typing":
                        # Typing indicator
                        await self.update_typing_status(
                            room_id=room_id,
                            user_id=int(user_id),
                            is_typing=message_data.get("is_typing", False),
                        )
                    else:
                        # Echo other messages back
                        await websocket.send_text(f"Received: {data}")

                except json.JSONDecodeError:
                    await websocket.send_text("Invalid JSON format")

        except Exception:
            # Remove connection from room
            if (
                room_id in self.active_connections
                and websocket in self.active_connections[room_id]
            ):
                self.active_connections[room_id].remove(websocket)

            # Remove user from presence tracking
            if user_id in self.user_presence[room_id]:
                self.user_presence[room_id].discard(user_id)
                self.chat_rooms[room_id]["online_members"] = len(
                    self.user_presence[room_id]
                )
                # Broadcast presence change would need username here
