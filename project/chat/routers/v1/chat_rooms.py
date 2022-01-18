from typing import List

from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from accounts.models import User
from chat.dependencies import chat_rooms as chat_room_dependencies
from chat.schemas import chat_rooms as chat_room_schemas
from chat.services import chat_rooms as chat_room_crud
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
        return await chat_room_crud.create_chat_room(name, members, self.db_session, **chat_room_data)

    @router.get('/chat_rooms', response_model=List[chat_room_schemas.ChatRoomListSchema])
    async def list_chat_rooms_view(self):
        return await chat_room_crud.get_chat_rooms(self.db_session, self.queryset)

    @router.get('/chat_rooms/{chat_room_id}', response_model=chat_room_schemas.ChatRoomDetailSchema)
    async def retrieve_chat_room_view(self, chat_room_id: int):
        return await chat_room_crud.get_chat_room(
            chat_room_id, self.db_session, queryset=self.queryset
        )

    @router.patch('/chat_rooms/{chat_room_id}', response_model=chat_room_schemas.ChatRoomDetailSchema)
    async def update_chat_room_view(self, chat_room_id: int, chat_room_data: chat_room_schemas.ChatRoomUpdateSchema):
        chat_room = await chat_room_crud.get_chat_room(
            chat_room_id, self.db_session, queryset=self.queryset
        )
        chat_room_data: dict = chat_room_data.dict(exclude_unset=True)
        members = chat_room_data.pop('members', None)
        if members:
            select_members_query = select(User).where(User.id.in_(members))
            members = await self.db_session.execute(select_members_query)
            members = members.scalars().all()
        return await chat_room_crud.update_chat_room(
            chat_room, self.db_session, members=members, **chat_room_data
        )
