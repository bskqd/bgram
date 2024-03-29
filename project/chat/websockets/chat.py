import json
from datetime import datetime

from accounts.models import User
from chat.services.chat_rooms import ChatRoomsRetrieveServiceABC
from core.dependencies.providers import EventPublisher, EventReceiver
from fastapi import WebSocket
from starlette.websockets import WebSocketState


class WebSocketConnection:
    def __init__(self, websocket: WebSocket, user: User, connected_at: datetime = datetime.now()):
        self.websocket = websocket
        self.user = user
        self.connected_at = connected_at


class ChatRoomsWebSocketConnectionManager:
    def __init__(self, websocket_connection: WebSocketConnection, event_receiver: EventReceiver):
        self.websocket_connection = websocket_connection
        self.event_receiver = event_receiver

    async def receive_messages(self, chat_rooms_retrieve_service: ChatRoomsRetrieveServiceABC):
        if self.websocket_connection.websocket.client_state != WebSocketState.CONNECTED:
            await self.accept_connection()
        chat_room_ids = await chat_rooms_retrieve_service.get_user_chat_room_ids(self.websocket_connection.user)
        await self.event_receiver.subscribe(*(f'chat_room:{chat_room_id}' for chat_room_id in chat_room_ids))
        async for message in self.event_receiver.listen():
            if message and message.get('type') != 'subscribe' and (data := message.get('data')):
                await self.send_personal_message(json.loads(data.decode('utf-8')))

    async def accept_connection(self):
        await self.websocket_connection.websocket.accept()

    async def disconnect(self):
        if self.websocket_connection.websocket.client_state != WebSocketState.DISCONNECTED:
            await self.websocket_connection.websocket.close()
        await self.event_receiver.unsubscribe()

    @classmethod
    async def broadcast(cls, message: dict, chat_room_id: int, event_publisher: EventPublisher):
        await event_publisher.publish(f'chat_room:{chat_room_id}', json.dumps(message, default=str))

    async def send_personal_message(self, message: dict):
        await self.websocket_connection.websocket.send_json(message)
