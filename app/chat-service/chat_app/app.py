"""FastAPI application setup"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from chat_app.routes import router
from chat_app.websocket import WebSocketManager
from chat_app.services import ChatService


# Initialize FastAPI app
app = FastAPI(title="Advanced Chat Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
chat_service = ChatService()
websocket_manager = WebSocketManager(chat_service)

# Include API routes
app.include_router(router)


@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket_manager.handle_connection(websocket, room_id, user_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)