from typing import List

from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from chat.dependencies import messages as messages_dependencies
from chat.schemas.messages import MessageInChatSchema
from chat.services.messages import MessagesService
from mixins import views as mixins_views, dependencies as mixins_dependencies

router = APIRouter()


@cbv(router)
class MessagesView(mixins_views.AbstractView):
    queryset: Select = Depends(messages_dependencies.get_messages_queryset)
    db_session: Session = Depends(mixins_dependencies.db_session)

    @router.get('/chat_rooms/{chat_room_id}/messages', response_model=List[MessageInChatSchema])
    async def list_messages_view(self, chat_room_id: int):
        return await MessagesService(self.db_session).list_messages(chat_room_id, self.queryset)
