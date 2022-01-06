from typing import Optional, Union

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from chat.constants.messages import MessagesActionTypeEnum
from chat.models import Message
from chat.schemas import messages as messages_schemas
from mixins.services import crud as mixins_crud_services


class MessagesService:
    """
    Service class for creating messages.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def process_received_message(
            self,
            message_data: messages_schemas.SendMessageInChatSchema,
            chat_room_id: int,
            author_id: Optional[int] = None
    ) -> Union[Message, int]:
        message_data = message_data.dict()
        message_id: Optional[int] = message_data.pop('message_id', None)
        action: str = message_data.pop('action')
        if action == MessagesActionTypeEnum.CREATE.value:
            return await self.create_message(chat_room_id, message_data.pop('text'), author_id, **message_data)
        elif action == MessagesActionTypeEnum.UPDATE.value:
            return await self.update_message(message_id, **message_data)
        elif action == MessagesActionTypeEnum.DELETE.value:
            return await self.delete_message(message_id)

    async def create_message(self, chat_room_id: int, text: str, author_id: Optional[int] = None, **kwargs) -> Message:
        message = Message(chat_room_id=chat_room_id, text=text, author_id=author_id, **kwargs)
        crud_operations_service = mixins_crud_services.CRUDOperationsService(self.db_session)
        new_message = await crud_operations_service.create_object_in_database(message)
        return await crud_operations_service.get_object(select(Message), Message, new_message.id)

    async def update_message(self, message: Union[int, Message], **kwargs) -> Message:
        crud_service = mixins_crud_services.CRUDOperationsService(self.db_session)
        if isinstance(message, int):
            message: Message = await crud_service.get_object(select(Message), Message, message)
        kwargs['is_edited'] = True
        return await crud_service.update_object_in_database(message, **kwargs)

    async def delete_message(self, message_id: int) -> int:
        await self.db_session.execute(delete(Message).where(Message.id == message_id))
        return message_id
