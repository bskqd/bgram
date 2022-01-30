from typing import List

from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from accounts.models import User
from chat.dependencies import chat_rooms as chat_room_dependencies
from chat.schemas import chat_rooms as chat_room_schemas
from chat.services.chat_rooms import ChatRoomService
from mixins import views as mixins_views, dependencies as mixins_dependencies

router = APIRouter()


@cbv(router)
class ChatRoomView(mixins_views.AbstractView):
    queryset: Select = Depends(chat_room_dependencies.get_available_chat_rooms_for_user)
    db_session: Session = Depends(mixins_dependencies.db_session)

    @router.post('/chat_rooms', response_model=chat_room_schemas.ChatRoomDetailSchema)
    async def create_chat_room_view(self, chat_room_data: chat_room_schemas.ChatRoomCreateSchema):
        chat_room_data = chat_room_data.dict()
        name = chat_room_data.pop('name')
        members = chat_room_data.pop('members', [])
        return await ChatRoomService(self.db_session).create_chat_room(name, members, **chat_room_data)

    @router.get('/chat_rooms', response_model=List[chat_room_schemas.ChatRoomListSchema])
    async def list_chat_rooms_view(self):
        return await ChatRoomService(self.db_session).list_chat_rooms(queryset=self.queryset)

    @router.get('/chat_rooms/{chat_room_id}', response_model=chat_room_schemas.ChatRoomDetailSchema)
    async def retrieve_chat_room_view(self, chat_room_id: int):
        return await ChatRoomService(self.db_session).retrieve_chat_room(chat_room_id, queryset=self.queryset)

    @router.patch('/chat_rooms/{chat_room_id}', response_model=chat_room_schemas.ChatRoomDetailSchema)
    async def update_chat_room_view(self, chat_room_id: int, chat_room_data: chat_room_schemas.ChatRoomUpdateSchema):
        chat_room_service = ChatRoomService(self.db_session)
        chat_room = await chat_room_service.retrieve_chat_room(chat_room_id, queryset=self.queryset)
        chat_room_data: dict = chat_room_data.dict(exclude_unset=True)
        members = chat_room_data.pop('members', None)
        if members:
            select_members_query = select(User).where(User.id.in_(members))
            members = await self.db_session.scalars(select_members_query)
            members = members.all()
        return await chat_room_service.update_chat_room(chat_room, members=members, **chat_room_data)
