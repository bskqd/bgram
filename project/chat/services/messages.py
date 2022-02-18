from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import WebSocket
from sqlalchemy.sql import Select

from accounts.models import User
from chat.constants.messages import MessagesActionTypeEnum
from chat.models import Message
from chat.schemas.messages import ListMessagesSchema
from database.repository import SQLAlchemyCRUDRepository


class WebSocketConnection:
    def __init__(self, websocket: WebSocket, user: User, chat_room_id: int, connected_at: datetime = datetime.now()):
        self.websocket = websocket
        self.user = user
        self.chat_room_id = chat_room_id
        self.connected_at = connected_at


class ChatRoomsWebSocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocketConnection]] = defaultdict(list)

    async def connect(self, websocket_connection: WebSocketConnection):
        await websocket_connection.websocket.accept()
        self.active_connections[websocket_connection.chat_room_id].append(websocket_connection)

    async def disconnect(self, websocket_connection: WebSocketConnection):
        await websocket_connection.websocket.close()
        chat_room_connections: List[WebSocketConnection] = self.active_connections[websocket_connection.chat_room_id]
        if websocket_connection in chat_room_connections:
            chat_room_connections.remove(websocket_connection)

    async def broadcast(self, message: dict, chat_room_id: int):
        for connection in self.active_connections[chat_room_id]:
            await self.send_personal_message(connection, message)

    async def send_personal_message(self, websocket_connection: WebSocketConnection, message: dict):
        await websocket_connection.websocket.send_json(message)


chat_rooms_websocket_manager = ChatRoomsWebSocketConnectionManager()


class MessagesService:
    def __init__(
            self,
            db_repository: SQLAlchemyCRUDRepository,
            chat_room_id: Optional[int] = None
    ):
        self.db_repository = db_repository
        self.chat_room_id = chat_room_id

    async def create_message(self, text: str, author_id: Optional[int] = None, **kwargs) -> Message:
        message = Message(chat_room_id=self.chat_room_id, text=text, author_id=author_id, **kwargs)
        created_message = await self.db_repository.create(message)
        await self.db_repository.commit()
        await self.db_repository.refresh(created_message)
        await self._broadcast_message_to_chat_room(
            self.chat_room_id, MessagesActionTypeEnum.CREATED.value, ListMessagesSchema.from_orm(created_message).dict()
        )
        return created_message

    async def update_message(self, message: Message, **kwargs) -> Message:
        if not message.is_edited:
            kwargs['is_edited'] = True
        updated_message = await self.db_repository.update_object(message, **kwargs)
        await self.db_repository.commit()
        await self.db_repository.refresh(updated_message)
        await self._broadcast_message_to_chat_room(
            self.chat_room_id, MessagesActionTypeEnum.UPDATED.value, ListMessagesSchema.from_orm(updated_message).dict()
        )
        return updated_message

    async def delete_message(self, message_id: int) -> int:
        await self.db_repository.delete(Message.id == message_id)
        await self._broadcast_message_to_chat_room(
            self.chat_room_id, MessagesActionTypeEnum.DELETED.value, {'message_id': message_id},
        )
        return message_id

    async def _broadcast_message_to_chat_room(self, chat_room_id: int, action: str, message_data: dict):
        await chat_rooms_websocket_manager.broadcast({'action': action, **message_data}, chat_room_id)
