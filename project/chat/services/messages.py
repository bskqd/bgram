from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Iterator, Union

from fastapi import WebSocket
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from accounts.models import User
from chat.constants.messages import MessagesActionTypeEnum
from chat.models import Message
from chat.schemas.messages import ListMessagesSchema
from mixins.services.crud import CRUDOperationsService


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
            db_session: Session,
            chat_room_id: Optional[int] = None,
            broadcast_action_to_chat_room: bool = True
    ):
        self.db_session = db_session
        self.chat_room_id = chat_room_id
        self.broadcast_action_to_chat_room = broadcast_action_to_chat_room

    async def list_messages(
            self,
            chat_room_id: Optional[int] = None,
            queryset: Select = select(Message)
    ) -> Iterator[Message]:
        if chat_room_id:
            queryset = queryset.where(Message.chat_room_id == chat_room_id)
        messages = await self.db_session.scalars(queryset)
        return messages.all()

    async def create_message(self, chat_room_id: int, text: str, author_id: Optional[int] = None, **kwargs) -> Message:
        message = Message(chat_room_id=chat_room_id, text=text, author_id=author_id, **kwargs)
        created_message = await CRUDOperationsService(self.db_session).create_object_in_database(message)
        if self.broadcast_action_to_chat_room:
            await self._broadcast_action_to_chat_room(
                chat_room_id, MessagesActionTypeEnum.CREATED.value, ListMessagesSchema.from_orm(created_message).dict(),
            )
        return created_message

    async def update_message(self, message: Union[int, Message], **kwargs) -> Message:
        crud_service = CRUDOperationsService(self.db_session)
        if isinstance(message, int):
            message: Message = await crud_service.get_object(select(Message), Message, message)
        kwargs['is_edited'] = True
        updated_message = await crud_service.update_object_in_database(message, **kwargs)
        if self.broadcast_action_to_chat_room:
            await self._broadcast_action_to_chat_room(
                self.chat_room_id, MessagesActionTypeEnum.UPDATED.value,
                ListMessagesSchema.from_orm(updated_message).dict(),
            )
        return updated_message

    async def delete_message(self, message_id: int) -> int:
        await self.db_session.execute(delete(Message).where(Message.id == message_id))
        if self.broadcast_action_to_chat_room:
            await self._broadcast_action_to_chat_room(
                self.chat_room_id, MessagesActionTypeEnum.DELETED.value, {'message_id': message_id},
            )
        return message_id

    async def _broadcast_action_to_chat_room(self, chat_room_id: int, action: str, message_data: dict):
        await chat_rooms_websocket_manager.broadcast(
            message={'action': action, **message_data},
            chat_room_id=chat_room_id
        )
