import json
from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from fastapi import WebSocket

from accounts.models import User
from core.dependencies import EventReceiver, EventPublisher


class WebSocketConnection:
    def __init__(self, websocket: WebSocket, user: User, chat_room_id: int, connected_at: datetime = datetime.now()):
        self.websocket = websocket
        self.user = user
        self.chat_room_id = chat_room_id
        self.connected_at = connected_at


class ChatRoomsWebSocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocketConnection]] = defaultdict(list)

    async def connect(self, websocket_connection: WebSocketConnection, event_receiver: EventReceiver):
        await websocket_connection.websocket.accept()
        channel = await event_receiver.subscribe(f'chat_room:{websocket_connection.chat_room_id}')
        while True:
            message = await channel.get()
            if message:
                await self.send_personal_message(websocket_connection, json.loads(message))
        # self.active_connections[websocket_connection.chat_room_id].append(websocket_connection)

    async def disconnect(self, websocket_connection: WebSocketConnection, event_receiver: EventReceiver):
        await websocket_connection.websocket.close()
        await event_receiver.unsubscribe()
        # chat_room_connections: List[WebSocketConnection] = self.active_connections[websocket_connection.chat_room_id]
        # if websocket_connection in chat_room_connections:
        #     chat_room_connections.remove(websocket_connection)

    async def broadcast(self, message: dict, chat_room_id: int, event_publisher: EventPublisher):
        await event_publisher.publish(f'chat_room:{chat_room_id}', json.dumps(message))
        # for connection in self.active_connections[chat_room_id]:
        #     await self.send_personal_message(connection, message)

    async def send_personal_message(self, websocket_connection: WebSocketConnection, message: dict):
        await websocket_connection.websocket.send_json(message)


chat_rooms_websocket_manager = ChatRoomsWebSocketConnectionManager()
