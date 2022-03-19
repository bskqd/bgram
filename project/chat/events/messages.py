from typing import Union

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from chat.constants.messages import MessagesActionTypeEnum
from chat.models import Message
from chat.schemas.messages import ListMessagesSchema
from chat.websockets.chat import chat_rooms_websocket_manager
from database.repository import BaseCRUDRepository


async def message_created_event(message: Union[Message, int], db_repository: BaseCRUDRepository):
    if isinstance(message, int):
        message = await _get_message(message, db_repository)
    await broadcast_message_to_chat_room(
        message.chat_room_id, MessagesActionTypeEnum.CREATED.value, ListMessagesSchema.from_orm(message).dict()
    )


async def message_updated_event(message: Union[Message, int], db_repository: BaseCRUDRepository):
    if isinstance(message, int):
        message = await _get_message(message, db_repository)
    await broadcast_message_to_chat_room(
        message.chat_room_id, MessagesActionTypeEnum.UPDATED.value, ListMessagesSchema.from_orm(message).dict()
    )


async def _get_message(message_id: int, db_repository: BaseCRUDRepository) -> Message:
    db_repository.db_query = select(Message).options(joinedload(Message.photos))
    return await db_repository.get_one(Message.id == message_id)


async def message_deleted_event(chat_room_id: int, message_id: int):
    await broadcast_message_to_chat_room(chat_room_id, MessagesActionTypeEnum.DELETED.value, {'message_id': message_id})


async def broadcast_message_to_chat_room(chat_room_id: int, action: str, message_data: dict):
    message_data['action'] = action
    await chat_rooms_websocket_manager.broadcast(message_data, chat_room_id)
