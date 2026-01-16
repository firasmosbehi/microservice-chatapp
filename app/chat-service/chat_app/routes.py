"""API routes for chat service"""

from fastapi import APIRouter, HTTPException
from typing import List

from .models import (
    CreateRoomRequest,
    JoinRoomRequest,
    MessageRequest,
    RoomResponse,
    TypingRequest,
    MessageReaction,
)
from .services import ChatService


# Initialize router and service
router = APIRouter(prefix="/api")
chat_service = ChatService()


@router.get("/", response_model=dict)
def read_root() -> dict:
    """Health check endpoint"""
    return {
        "message": "Advanced Chat Service Running",
        "version": "2.0.0",
        "features": [
            "Real-time messaging",
            "User presence tracking",
            "Typing indicators",
            "Message reactions",
            "Threaded conversations",
            "Private rooms",
        ],
    }


@router.post("/rooms", response_model=RoomResponse)
def create_room(request: CreateRoomRequest) -> RoomResponse:
    """Create a new chat room"""
    try:
        room_data = chat_service.create_room(
            name=request.name,
            creator_id=request.creator_id,
            description=request.description,
            is_private=request.is_private,
            invited_users=request.invited_users,
        )

        return RoomResponse(
            id=room_data["id"],
            name=room_data["name"],
            description=room_data["description"],
            creator_id=room_data["creator_id"],
            created_at=room_data["created_at"],
            member_count=room_data["member_count"],
            is_private=room_data["is_private"],
            online_members=room_data["online_members"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms", response_model=List[RoomResponse])
def get_rooms() -> List[RoomResponse]:
    """Get all chat rooms"""
    try:
        rooms = chat_service.get_all_rooms()
        return [RoomResponse(**room) for room in rooms]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms/{room_id}", response_model=RoomResponse)
def get_room(room_id: str) -> RoomResponse:
    """Get specific room details"""
    try:
        room = chat_service.get_room(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")

        return RoomResponse(
            id=room["id"],
            name=room["name"],
            description=room["description"],
            creator_id=room["creator_id"],
            created_at=room["created_at"],
            member_count=room["member_count"],
            is_private=room["is_private"],
            online_members=len(chat_service.user_presence.get(room_id, set())),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rooms/{room_id}/join")
async def join_room(room_id: str, request: JoinRoomRequest) -> dict:
    """Join a chat room"""
    try:
        room_info = await chat_service.join_room(
            room_id=room_id, user_id=request.user_id, username=request.username
        )

        return {"message": "Successfully joined room", "room": room_info}
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rooms/{room_id}/leave")
async def leave_room(room_id: str, request: JoinRoomRequest) -> dict:
    """Leave a chat room"""
    try:
        await chat_service.leave_room(
            room_id=room_id, user_id=request.user_id, username=request.username
        )
        return {"message": "Successfully left room"}
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages")
async def send_message(request: MessageRequest) -> dict:
    """Send a message to a chat room"""
    try:
        message_id = await chat_service.send_message(
            room_id=request.room_id,
            user_id=request.user_id,
            username=request.username,
            content=request.content,
            message_type=request.message_type,
            parent_id=request.parent_id,
        )

        return {"message": "Message sent successfully", "message_id": message_id}
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        elif "not in room" in str(e).lower():
            raise HTTPException(status_code=403, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms/{room_id}/messages")
def get_room_messages(room_id: str, limit: int = 50, offset: int = 0) -> list:
    """Get messages for a specific room"""
    try:
        messages = chat_service.get_room_messages(
            room_id=room_id, limit=limit, offset=offset
        )
        return messages
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/typing")
async def update_typing_status(request: TypingRequest) -> dict:
    """Update typing status for a user in a room"""
    try:
        await chat_service.update_typing_status(
            room_id=request.room_id,
            user_id=request.user_id,
            is_typing=request.is_typing,
        )
        return {"message": "Typing status updated"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reactions")
async def add_reaction(reaction: MessageReaction) -> dict:
    """Add reaction to a message"""
    try:
        reactions = await chat_service.add_reaction(
            message_id=reaction.message_id,
            user_id=reaction.user_id,
            reaction=reaction.reaction,
        )
        return {"message": "Reaction added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
