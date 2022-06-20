import json
from datetime import datetime

from fastapi import WebSocket

from accounts.models import User
from core.dependencies import EventReceiver, EventPublisher


class WebSocketConnection:
    def __init__(self, websocket: WebSocket, user: User, connected_at: datetime = datetime.now()):
        self.websocket = websocket
        self.user = user
        self.connected_at = connected_at


class ChatRoomsWebSocketConnectionManager:
    async def connect(
            self,
            websocket_connection: WebSocketConnection,
            event_receiver: EventReceiver,
            chat_rooms_retrieve_service,
    ):
        await websocket_connection.websocket.accept()
        chat_room_ids = await chat_rooms_retrieve_service.get_user_chat_room_ids(websocket_connection.user)
        await event_receiver.subscribe(*(f'chat_room:{chat_room_id}' for chat_room_id in chat_room_ids))
        async for message in event_receiver.listen():
            if message and message.get('type') != 'subscribe' and (data := message.get('data')):
                await self.send_personal_message(websocket_connection, json.loads(data.decode('utf-8')))

    async def disconnect(self, websocket_connection: WebSocketConnection, event_receiver: EventReceiver):
        await websocket_connection.websocket.close()
        await event_receiver.unsubscribe()

    async def broadcast(self, message: dict, chat_room_id: int, event_publisher: EventPublisher):
        await event_publisher.publish(f'chat_room:{chat_room_id}', json.dumps(message))

    async def send_personal_message(self, websocket_connection: WebSocketConnection, message: dict):
        await websocket_connection.websocket.send_json(message)


chat_rooms_websocket_manager = ChatRoomsWebSocketConnectionManager()
