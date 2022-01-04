from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from chat.models import Message
from mixins.services import crud as mixins_crud_services


class MessagesCreatingService:
    """
    Service class for creating messages.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_message(self, chat_room_id: int, text: str, author_id: Optional[int] = None, **kwargs):
        message = Message(chat_room_id=chat_room_id, text=text, author_id=author_id, **kwargs)
        crud_operations_service = mixins_crud_services.CRUDOperationsService(self.db_session)
        new_message = await crud_operations_service.create_object_in_database(message)
        return await crud_operations_service.get_object(select(Message), Message, new_message.id)
