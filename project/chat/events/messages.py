from typing import Union

from chat.api.v1.schemas.messages import ListMessagesSchema
from chat.constants.messages import MessagesActionTypeEnum
from chat.models import Message
from chat.websockets.chat import ChatRoomsWebSocketConnectionManager
from core.dependencies import EventPublisher


async def message_created_event(event_publisher: EventPublisher, message: Union[Message, int]):
    await broadcast_message_to_chat_room(
        event_publisher, message.chat_room_id,
        MessagesActionTypeEnum.CREATED.value, ListMessagesSchema.from_orm(message).dict(),
    )


async def message_updated_event(event_publisher: EventPublisher, message: Message):
    await broadcast_message_to_chat_room(
        event_publisher, message.chat_room_id,
        MessagesActionTypeEnum.UPDATED.value, ListMessagesSchema.from_orm(message).dict(),
    )


async def messages_deleted_event(event_publisher: EventPublisher, chat_room_id: int, message_ids: tuple[int]):
    await broadcast_message_to_chat_room(
        event_publisher, chat_room_id, MessagesActionTypeEnum.DELETED.value, {'message_ids': message_ids},
    )


async def broadcast_message_to_chat_room(
        event_publisher: EventPublisher,
        chat_room_id: int,
        action: str,
        message_data: dict,
):
    message_data['action'] = action
    await ChatRoomsWebSocketConnectionManager.broadcast(message_data, chat_room_id, event_publisher)
