import structlog
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Optional
from app.shared.security.tokens import decode_token

logger = structlog.get_logger()

class WebSocketConnectionManager:
    def __init__(self):
        # Maps user_id to active WebSocket instances
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.rooms: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, token: str) -> Optional[str]:
        """Validates connection access token, registers connection, and opens socket."""
        try:
            payload = decode_token(token)
            user_id = payload.get("sub")
            token_type = payload.get("type")
            if not user_id or token_type != "access":
                await websocket.close(code=4001)
                return None
        except Exception:
            await websocket.close(code=4001)
            return None

        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        logger.info("WebSocket connection registered", user_id=user_id)
        return user_id

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        """Gracefully discards the active websocket connection instance."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info("WebSocket connection closed", user_id=user_id)

    async def send_personal_message(self, message: dict, user_id: str) -> None:
        """Pushes JSON event payload to specific user's connected socket interfaces."""
        sockets = self.active_connections.get(user_id, set())
        for socket in list(sockets):
            try:
                await socket.send_json(message)
            except Exception as e:
                logger.error(
                    "WebSocket transmission failed",
                    user_id=user_id,
                    error=str(e)
                )
                self.disconnect(user_id, socket)

    async def broadcast_to_room(self, room_id: str, message: dict) -> None:
        """Broadcasts payload to all users registered in the channel room."""
        users = self.rooms.get(room_id, set())
        for user_id in list(users):
            await self.send_personal_message(message, user_id)

    def join_room(self, user_id: str, room_id: str) -> None:
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(user_id)

    def leave_room(self, user_id: str, room_id: str) -> None:
        if room_id in self.rooms:
            self.rooms[room_id].discard(user_id)
            if not self.rooms[room_id]:
                del self.rooms[room_id]

# Global WS Manager Instance
ws_manager = WebSocketConnectionManager()
