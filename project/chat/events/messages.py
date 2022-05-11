from typing import Union

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from chat.api.v1.schemas.messages import ListMessagesSchema
from chat.constants.messages import MessagesActionTypeEnum
from chat.models import Message
from chat.websockets.chat import chat_rooms_websocket_manager
from core.dependencies import EventPublisher
from core.database.repository import BaseCRUDRepository


async def message_created_event(
        event_publisher: EventPublisher,
        message: Union[Message, int],
        db_repository: BaseCRUDRepository
):
    if isinstance(message, int):
        message = await _get_message(message, db_repository)
    await broadcast_message_to_chat_room(
        event_publisher, message.chat_room_id,
        MessagesActionTypeEnum.CREATED.value, ListMessagesSchema.from_orm(message).dict()
    )


async def message_updated_event(
        event_publisher: EventPublisher,
        message: Union[Message, int],
        db_repository: BaseCRUDRepository
):
    if isinstance(message, int):
        message = await _get_message(message, db_repository)
    await broadcast_message_to_chat_room(
        event_publisher, message.chat_room_id,
        MessagesActionTypeEnum.UPDATED.value, ListMessagesSchema.from_orm(message).dict()
    )


async def _get_message(message_id: int, db_repository: BaseCRUDRepository) -> Message:
    db_repository.db_query = select(Message).options(joinedload(Message.photos))
    message = await db_repository.get_one(Message.id == message_id)
    db_repository.db_query = None
    return message


async def messages_deleted_event(event_publisher: EventPublisher, chat_room_id: int, message_ids: list[int]):
    await broadcast_message_to_chat_room(
        event_publisher, chat_room_id, MessagesActionTypeEnum.DELETED.value, {'message_ids': message_ids}
    )


async def broadcast_message_to_chat_room(
        event_publisher: EventPublisher,
        chat_room_id: int,
        action: str,
        message_data: dict
):
    message_data['action'] = action
    await chat_rooms_websocket_manager.broadcast(message_data, chat_room_id, event_publisher)
