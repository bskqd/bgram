from typing import Optional, Union, Iterator

from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from chat.models import Message
from mixins.services.crud import CRUDOperationsService


class MessagesService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def list_messages(self, chat_room_id: int, queryset: Select = select(Message)) -> Iterator[Message]:
        queryset = queryset.where(Message.chat_room_id == chat_room_id)
        messages = await self.db_session.execute(queryset)
        return messages.scalars().all()

    async def create_message(self, chat_room_id: int, text: str, author_id: Optional[int] = None, **kwargs) -> Message:
        message = Message(chat_room_id=chat_room_id, text=text, author_id=author_id, **kwargs)
        crud_operations_service = CRUDOperationsService(self.db_session)
        return await crud_operations_service.create_object_in_database(message)

    async def update_message(self, message: Union[int, Message], **kwargs) -> Message:
        crud_service = CRUDOperationsService(self.db_session)
        if isinstance(message, int):
            message: Message = await crud_service.get_object(select(Message), Message, message)
        kwargs['is_edited'] = True
        return await crud_service.update_object_in_database(message, **kwargs)

    async def delete_message(self, message_id: int) -> int:
        await self.db_session.execute(delete(Message).where(Message.id == message_id))
        return message_id
