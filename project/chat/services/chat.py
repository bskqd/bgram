from typing import Optional, Union

from sqlalchemy.orm import Session

from chat.constants.messages import MessagesActionTypeEnum
from chat.models import Message
from chat.schemas.messages import SendMessageInChatSchema
from chat.services.messages import MessagesService


class ChatService:
    """
    Service class for creating messages.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def process_received_message(
            self,
            message_data: SendMessageInChatSchema,
            chat_room_id: int,
            author_id: Optional[int] = None
    ) -> Union[Message, int]:
        message_data = message_data.dict()
        message_id: Optional[int] = message_data.pop('message_id', None)
        action: str = message_data.pop('action')
        messages_service_instance = MessagesService(db_session=self.db_session)
        if action == MessagesActionTypeEnum.CREATE.value:
            return await messages_service_instance.create_message(
                chat_room_id, message_data.pop('text'), author_id, **message_data
            )
        elif action == MessagesActionTypeEnum.UPDATE.value:
            return await messages_service_instance.update_message(message_id, **message_data)
        elif action == MessagesActionTypeEnum.DELETE.value:
            return await messages_service_instance.delete_message(message_id)
