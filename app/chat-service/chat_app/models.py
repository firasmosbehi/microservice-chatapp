"""Pydantic models for chat service"""

from pydantic import BaseModel
from typing import List, Optional


class CreateRoomRequest(BaseModel):
    """Request model for creating a new chat room"""
    name: str
    creator_id: int
    description: Optional[str] = None
    is_private: bool = False
    invited_users: Optional[List[int]] = None


class JoinRoomRequest(BaseModel):
    """Request model for joining a chat room"""
    user_id: int
    username: str


class MessageRequest(BaseModel):
    """Request model for sending a message"""
    room_id: str
    user_id: int
    username: str
    content: str
    message_type: str = "text"  # text, image, file, system
    parent_id: Optional[str] = None  # for replies


class RoomResponse(BaseModel):
    """Response model for room information"""
    id: str
    name: str
    description: Optional[str]
    creator_id: int
    created_at: str
    member_count: int
    is_private: bool
    online_members: int


class TypingRequest(BaseModel):
    """Request model for typing indicators"""
    room_id: str
    user_id: int
    username: str
    is_typing: bool


class MessageReaction(BaseModel):
    """Model for message reactions"""
    message_id: str
    user_id: int
    reaction: str  # emoji or reaction type