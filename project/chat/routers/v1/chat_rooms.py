from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select

from accounts.models import User
from chat.models import ChatRoom, chatroom_members_association_table
from chat.schemas.chat_rooms import (PaginatedChatRoomsListSchema, ChatRoomDetailSchema, ChatRoomCreateSchema,
                                     ChatRoomUpdateSchema)
from chat.services.chat_rooms import ChatRoomService
from mixins import views as mixins_views, dependencies as mixins_dependencies
from mixins.pagination import DefaultPaginationClass
from mixins.permissions import UserIsAuthenticatedPermission

router = APIRouter()


@cbv(router)
class ChatRoomView(mixins_views.AbstractView):
    db_session: AsyncSession = Depends(mixins_dependencies.db_session)
    pagination_class = DefaultPaginationClass

    async def check_permissions(self):
        await UserIsAuthenticatedPermission(self.request_user).check_permissions()

    def get_db_query(self) -> Select:
        return select(
            ChatRoom
        ).join(
            chatroom_members_association_table
        ).options(
            joinedload(ChatRoom.members).load_only(User.id), joinedload(ChatRoom.photos)
        ).where(
            chatroom_members_association_table.c.user_id == self.request_user.id
        )

    @router.get('/chat_rooms', response_model=PaginatedChatRoomsListSchema)
    async def list_chat_rooms_view(self):
        await self.check_permissions()
        return self.get_paginated_response(
            await ChatRoomService(self.db_session).list_chat_rooms(db_query=self.get_db_query())
        )

    @router.get('/chat_rooms/{chat_room_id}', response_model=ChatRoomDetailSchema)
    async def retrieve_chat_room_view(self, chat_room_id: int):
        await self.check_permissions()
        return await ChatRoomService(self.db_session).retrieve_chat_room(chat_room_id, db_query=self.get_db_query())

    @router.post('/chat_rooms', response_model=ChatRoomDetailSchema)
    async def create_chat_room_view(self, chat_room_data: ChatRoomCreateSchema):
        await self.check_permissions()
        chat_room_data = chat_room_data.dict()
        name = chat_room_data.pop('name')
        members = chat_room_data.pop('members', [])
        return await ChatRoomService(self.db_session).create_chat_room(name, members, **chat_room_data)

    @router.patch('/chat_rooms/{chat_room_id}', response_model=ChatRoomDetailSchema)
    async def update_chat_room_view(self, chat_room_id: int, chat_room_data: ChatRoomUpdateSchema):
        await self.check_permissions()
        chat_room_service = ChatRoomService(self.db_session)
        chat_room = await chat_room_service.retrieve_chat_room(chat_room_id, db_query=self.get_db_query())
        chat_room_data: dict = chat_room_data.dict(exclude_unset=True)
        members = chat_room_data.pop('members', None)
        if members:
            select_members_query = select(User).where(User.id.in_(members))
            members = await self.db_session.scalars(select_members_query)
            members = members.all()
        return await chat_room_service.update_chat_room(chat_room, members=members, **chat_room_data)
