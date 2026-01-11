from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional, Set
from datetime import datetime
import json
import uuid
from collections import defaultdict
import asyncio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Advanced Chat Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced in-memory storage
chat_rooms: Dict[str, Dict] = {}
messages: Dict[str, List[Dict]] = defaultdict(list)
active_connections: Dict[str, List[WebSocket]] = defaultdict(list)
user_sessions: Dict[str, str] = {}  # user_id -> session_id
user_presence: Dict[str, Set[str]] = defaultdict(set)  # room_id -> set of user_ids
typing_users: Dict[str, Set[str]] = defaultdict(set)  # room_id -> set of typing user_ids

# Pydantic models
class CreateRoomRequest(BaseModel):
    name: str
    creator_id: int
    description: Optional[str] = None
    is_private: bool = False
    invited_users: Optional[List[int]] = None

class JoinRoomRequest(BaseModel):
    user_id: int
    username: str

class MessageRequest(BaseModel):
    room_id: str
    user_id: int
    username: str
    content: str
    message_type: str = "text"  # text, image, file, system
    parent_id: Optional[str] = None  # for replies

class RoomResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    creator_id: int
    created_at: str
    member_count: int
    is_private: bool
    online_members: int

class TypingRequest(BaseModel):
    room_id: str
    user_id: int
    username: str
    is_typing: bool

class MessageReaction(BaseModel):
    message_id: str
    user_id: int
    reaction: str  # emoji or reaction type

# Helper functions
async def broadcast_to_room(room_id: str, message: dict):
    """Broadcast message to all connections in a room"""
    if room_id in active_connections:
        disconnected = []
        for connection in active_connections[room_id]:
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            active_connections[room_id].remove(conn)

async def notify_user_presence(room_id: str, user_id: int, username: str, status: str):
    """Notify room about user presence changes"""
    presence_message = {
        "type": "presence_change",
        "user_id": user_id,
        "username": username,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    await broadcast_to_room(room_id, presence_message)

@app.get("/")
def read_root():
    return {
        "message": "Advanced Chat Service Running", 
        "version": "2.0.0",
        "features": [
            "Real-time messaging",
            "User presence tracking",
            "Typing indicators",
            "Message reactions",
            "Threaded conversations",
            "Private rooms"
        ]
    }

@app.post("/rooms", response_model=RoomResponse)
def create_room(request: CreateRoomRequest):
    """Create a new chat room"""
    room_id = str(uuid.uuid4())
    
    # Get creator username (you might want to fetch this from user service)
    creator_username = f"User_{request.creator_id}"  # Placeholder
    
    room_data = {
        "id": room_id,
        "name": request.name,
        "description": request.description,
        "creator_id": request.creator_id,
        "created_at": datetime.now().isoformat(),
        "members": {request.creator_id: creator_username},
        "member_count": 1,
        "is_private": request.is_private,
        "invited_users": request.invited_users or [],
        "online_members": 1
    }
    
    chat_rooms[room_id] = room_data
    messages[room_id] = []
    
    # Create system message
    system_msg = {
        "id": str(uuid.uuid4()),
        "room_id": room_id,
        "user_id": 0,
        "username": "System",
        "content": f"Room '{request.name}' created by User_{request.creator_id}",
        "timestamp": datetime.now().isoformat(),
        "type": "system"
    }
    
    messages[room_id].append(system_msg)
    
    return RoomResponse(
        id=room_data["id"],
        name=room_data["name"],
        description=room_data["description"],
        creator_id=room_data["creator_id"],
        created_at=room_data["created_at"],
        member_count=room_data["member_count"],
        is_private=room_data["is_private"],
        online_members=room_data["online_members"]
    )

@app.get("/rooms", response_model=List[RoomResponse])
def get_rooms():
    """Get all chat rooms"""
    return [
        RoomResponse(
            id=room["id"],
            name=room["name"],
            description=room["description"],
            creator_id=room["creator_id"],
            created_at=room["created_at"],
            member_count=room["member_count"],
            is_private=room["is_private"],
            online_members=len(user_presence.get(room["id"], set()))
        )
        for room in chat_rooms.values()
    ]

@app.get("/rooms/{room_id}", response_model=RoomResponse)
def get_room(room_id: str):
    """Get specific room details"""
    if room_id not in chat_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = chat_rooms[room_id]
    return RoomResponse(
        id=room["id"],
        name=room["name"],
        description=room["description"],
        creator_id=room["creator_id"],
        created_at=room["created_at"],
        member_count=room["member_count"],
        is_private=room["is_private"],
        online_members=len(user_presence.get(room_id, set()))
    )

@app.post("/rooms/{room_id}/join")
async def join_room(room_id: str, request: JoinRoomRequest):
    """Join a chat room"""
    if room_id not in chat_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Add user to room members
    chat_rooms[room_id]["members"][request.user_id] = request.username
    chat_rooms[room_id]["member_count"] = len(chat_rooms[room_id]["members"])
    
    # Track user presence
    user_presence[room_id].add(str(request.user_id))
    chat_rooms[room_id]["online_members"] = len(user_presence[room_id])
    
    # Create welcome message
    welcome_msg = {
        "id": str(uuid.uuid4()),
        "room_id": room_id,
        "user_id": request.user_id,
        "username": request.username,
        "content": f"{request.username} joined the room",
        "timestamp": datetime.now().isoformat(),
        "type": "system"
    }
    
    messages[room_id].append(welcome_msg)
    
    # Notify presence change
    await notify_user_presence(room_id, request.user_id, request.username, "joined")
    
    # Broadcast join event
    join_event = {
        "type": "user_joined",
        "user_id": request.user_id,
        "username": request.username,
        "room_id": room_id,
        "timestamp": datetime.now().isoformat()
    }
    await broadcast_to_room(room_id, join_event)
    
    # Broadcast welcome message
    message_event = {
        "type": "message",
        "message": welcome_msg
    }
    await broadcast_to_room(room_id, message_event)
    
    return {
        "message": "Successfully joined room", 
        "room": {
            "id": chat_rooms[room_id]["id"],
            "name": chat_rooms[room_id]["name"],
            "member_count": chat_rooms[room_id]["member_count"],
            "online_members": chat_rooms[room_id]["online_members"]
        }
    }

@app.post("/rooms/{room_id}/leave")
async def leave_room(room_id: str, request: JoinRoomRequest):
    """Leave a chat room"""
    if room_id not in chat_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if str(request.user_id) in user_presence[room_id]:
        # Remove from presence tracking
        user_presence[room_id].discard(str(request.user_id))
        chat_rooms[room_id]["online_members"] = len(user_presence[room_id])
        
        # Remove from typing indicators if typing
        typing_users[room_id].discard(str(request.user_id))
        
        # Create leave message
        leave_msg = {
            "id": str(uuid.uuid4()),
            "room_id": room_id,
            "user_id": request.user_id,
            "username": request.username,
            "content": f"{request.username} left the room",
            "timestamp": datetime.now().isoformat(),
            "type": "system"
        }
        
        messages[room_id].append(leave_msg)
        
        # Notify presence change
        await notify_user_presence(room_id, request.user_id, request.username, "left")
        
        # Broadcast leave event
        leave_event = {
            "type": "user_left",
            "user_id": request.user_id,
            "username": request.username,
            "room_id": room_id,
            "timestamp": datetime.now().isoformat()
        }
        await broadcast_to_room(room_id, leave_event)
        
        # Broadcast leave message
        message_event = {
            "type": "message",
            "message": leave_msg
        }
        await broadcast_to_room(room_id, message_event)
    
    return {"message": "Successfully left room"}

@app.post("/messages")
async def send_message(request: MessageRequest):
    """Send a message to a chat room"""
    if request.room_id not in chat_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if str(request.user_id) not in user_presence[request.room_id]:
        raise HTTPException(status_code=403, detail="User not in room")
    
    # Create message
    message = {
        "id": str(uuid.uuid4()),
        "room_id": request.room_id,
        "user_id": request.user_id,
        "username": request.username,
        "content": request.content,
        "timestamp": datetime.now().isoformat(),
        "type": request.message_type,
        "parent_id": request.parent_id,
        "reactions": {}
    }
    
    # Store message
    messages[request.room_id].append(message)
    
    # Broadcast message to room
    message_event = {
        "type": "message",
        "message": message
    }
    await broadcast_to_room(request.room_id, message_event)
    
    # Clear typing indicator for this user
    typing_users[request.room_id].discard(str(request.user_id))
    await broadcast_typing_status(request.room_id)
    
    return {"message": "Message sent successfully", "message_id": message["id"]}

@app.get("/rooms/{room_id}/messages")
def get_room_messages(room_id: str, limit: int = 50, offset: int = 0):
    """Get messages for a specific room"""
    if room_id not in chat_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room_messages = messages[room_id]
    # Return messages in reverse chronological order (newest first)
    return room_messages[::-1][offset:offset + limit]

@app.post("/typing")
async def update_typing_status(request: TypingRequest):
    """Update typing status for a user in a room"""
    if request.room_id not in chat_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if request.is_typing:
        typing_users[request.room_id].add(str(request.user_id))
    else:
        typing_users[request.room_id].discard(str(request.user_id))
    
    await broadcast_typing_status(request.room_id)
    return {"message": "Typing status updated"}

async def broadcast_typing_status(room_id: str):
    """Broadcast current typing users to the room"""
    typing_list = list(typing_users[room_id])
    typing_event = {
        "type": "typing_update",
        "room_id": room_id,
        "typing_users": typing_list,
        "timestamp": datetime.now().isoformat()
    }
    await broadcast_to_room(room_id, typing_event)

@app.post("/reactions")
async def add_reaction(reaction: MessageReaction):
    """Add reaction to a message"""
    # Find the message and add reaction
    for room_id, room_messages in messages.items():
        for msg in room_messages:
            if msg["id"] == reaction.message_id:
                if "reactions" not in msg:
                    msg["reactions"] = {}
                
                if reaction.reaction not in msg["reactions"]:
                    msg["reactions"][reaction.reaction] = []
                
                if reaction.user_id not in msg["reactions"][reaction.reaction]:
                    msg["reactions"][reaction.reaction].append(reaction.user_id)
                
                # Broadcast reaction update
                reaction_event = {
                    "type": "reaction_added",
                    "message_id": reaction.message_id,
                    "reaction": reaction.reaction,
                    "user_id": reaction.user_id,
                    "reactions": msg["reactions"]
                }
                await broadcast_to_room(room_id, reaction_event)
                return {"message": "Reaction added successfully"}
    
    raise HTTPException(status_code=404, detail="Message not found")

@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    """WebSocket endpoint for real-time chat"""
    if room_id not in chat_rooms:
        await websocket.close(code=4004, reason="Room not found")
        return
    
    await websocket.accept()
    
    # Add connection to room
    if room_id not in active_connections:
        active_connections[room_id] = []
    active_connections[room_id].append(websocket)
    
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
                    typing_req = TypingRequest(
                        room_id=room_id,
                        user_id=int(user_id),
                        username=message_data.get("username", ""),
                        is_typing=message_data.get("is_typing", False)
                    )
                    await update_typing_status(typing_req)
                else:
                    # Echo other messages back
                    await websocket.send_text(f"Received: {data}")
                    
            except json.JSONDecodeError:
                await websocket.send_text("Invalid JSON format")
                
    except WebSocketDisconnect:
        # Remove connection from room
        if room_id in active_connections and websocket in active_connections[room_id]:
            active_connections[room_id].remove(websocket)
        
        # Remove user from presence tracking
        if user_id in user_presence[room_id]:
            user_presence[room_id].discard(user_id)
            chat_rooms[room_id]["online_members"] = len(user_presence[room_id])
            # Broadcast presence change
            # (Implementation would depend on having username available here)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)