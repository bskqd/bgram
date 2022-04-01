from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select

from accounts.models import User
from chat.models import ChatRoom, chatroom_members_association_table
from chat.api.v1.schemas.chat_rooms import (PaginatedChatRoomsListSchema, ChatRoomDetailSchema, ChatRoomCreateSchema,
                                            ChatRoomUpdateSchema)
from chat.services.chat_rooms import ChatRoomService
from database.repository import SQLAlchemyCRUDRepository
from mixins import views as mixins_views
from mixins.pagination import DefaultPaginationClass
from mixins.permissions import UserIsAuthenticatedPermission

router = APIRouter()


@cbv(router)
class ChatRoomView(mixins_views.AbstractView):
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
        db_repository = SQLAlchemyCRUDRepository(ChatRoom, self.db_session, self.get_db_query())
        return await self.get_paginated_response(db_repository, self.get_db_query())

    @router.get('/chat_rooms/{chat_room_id}', response_model=ChatRoomDetailSchema)
    async def retrieve_chat_room_view(self, chat_room_id: int):
        await self.check_permissions()
        db_repository = SQLAlchemyCRUDRepository(ChatRoom, self.db_session, self.get_db_query())
        return await ChatRoomService(db_repository).retrieve_chat_room(ChatRoom.id == chat_room_id)

    @router.post('/chat_rooms', response_model=ChatRoomDetailSchema)
    async def create_chat_room_view(self, chat_room_data: ChatRoomCreateSchema):
        await self.check_permissions()
        chat_room_data = chat_room_data.dict()
        name = chat_room_data.pop('name')
        members = chat_room_data.pop('members', [])
        db_repository = SQLAlchemyCRUDRepository(ChatRoom, self.db_session)
        chat_room = await ChatRoomService(db_repository).create_chat_room(name, members, **chat_room_data)
        db_repository.db_query = select(ChatRoom).options(
            joinedload(ChatRoom.members).load_only(User.id), joinedload(ChatRoom.photos)
        )
        return await db_repository.get_one(ChatRoom.id == chat_room.id)

    @router.patch('/chat_rooms/{chat_room_id}', response_model=ChatRoomDetailSchema)
    async def update_chat_room_view(self, chat_room_id: int, chat_room_data: ChatRoomUpdateSchema):
        await self.check_permissions()
        db_repository = SQLAlchemyCRUDRepository(ChatRoom, self.db_session, self.get_db_query())
        chat_room = await db_repository.get_one(ChatRoom.id == chat_room_id)
        chat_room_data: dict = chat_room_data.dict(exclude_unset=True)
        members = chat_room_data.pop('members', None)
        if members:
            db_repository.db_query = select(User).where(User.id.in_(members))
            members = await db_repository.get_many()
            db_repository.db_query = None
        return await ChatRoomService(db_repository).update_chat_room(chat_room, members=members, **chat_room_data)
