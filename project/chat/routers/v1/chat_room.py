from typing import List

from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.orm import Session

from chat.crud import chat_room as chat_room_crud
from chat.dependencies import chat_room as chat_room_dependencies
from chat.schemas import chat_room as chat_room_schemas
from mixins import views as mixins_views, dependencies as mixins_dependencies

router = APIRouter()


@cbv(router)
class ChatRoomView(mixins_views.AbstractView):
    available_db_data: ChunkedIteratorResult = Depends(chat_room_dependencies.available_db_data)
    db_session: Session = Depends(mixins_dependencies.db_session)

    @router.post('/chat_rooms', response_model=chat_room_schemas.ChatRoom)
    async def create_chat_room_view(self, chat_room_data: chat_room_schemas.ChatRoomCreate):
        chat_room_data = chat_room_data.dict()
        name = chat_room_data.pop('name')
        members = chat_room_data.pop('members', [])
        return await chat_room_crud.create_chat_room(name, members, self.db_session, **chat_room_data)

    @router.get('/chat_rooms', response_model=List[chat_room_schemas.ChatRoom])
    async def get_chat_rooms_view(self):
        return await chat_room_crud.get_chat_rooms(self.db_session, self.available_db_data)
