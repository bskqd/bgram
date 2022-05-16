from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select

from accounts.models import User
from chat.api.permissions.chat_rooms import ChatRoomPermission
from chat.api.v1.schemas.chat_rooms import (
    PaginatedChatRoomsListSchema, ChatRoomDetailSchema, ChatRoomCreateSchema, ChatRoomUpdateSchema,
)
from chat.models import ChatRoom, chatroom_members_association_table
from chat.services.chat_rooms import ChatRoomService
from core.database.repository import SQLAlchemyCRUDRepository
from core.dependencies import get_paginator

router = APIRouter()


def get_chat_rooms_db_query(request_user: User) -> Select:
    return select(
        ChatRoom
    ).join(
        chatroom_members_association_table
    ).options(
        joinedload(ChatRoom.members).load_only(User.id), joinedload(ChatRoom.photos)
    ).where(
        chatroom_members_association_table.c.user_id == request_user.id
    )


@router.get('/chat_rooms', response_model=PaginatedChatRoomsListSchema)
async def list_chat_rooms_view(
        request_user: User = Depends(),
        db_session: AsyncSession = Depends(),
        paginator=Depends(get_paginator),
):
    await ChatRoomPermission(request_user).check_permissions()
    db_repository = SQLAlchemyCRUDRepository(ChatRoom, db_session)
    return await paginator.paginate(get_chat_rooms_db_query(request_user), db_repository)


@router.get('/chat_rooms/{chat_room_id}', response_model=ChatRoomDetailSchema)
async def retrieve_chat_room_view(
        chat_room_id: int,
        request_user: User = Depends(),
        db_session: AsyncSession = Depends(),
):
    await ChatRoomPermission(request_user).check_permissions()
    db_repository = SQLAlchemyCRUDRepository(ChatRoom, db_session, get_chat_rooms_db_query(request_user))
    return await ChatRoomService(db_repository).retrieve_chat_room(ChatRoom.id == chat_room_id)


@router.post('/chat_rooms', response_model=ChatRoomDetailSchema)
async def create_chat_room_view(
        chat_room_data: ChatRoomCreateSchema,
        request_user: User = Depends(),
        db_session: AsyncSession = Depends(),
):
    await ChatRoomPermission(request_user).check_permissions()
    chat_room_data = chat_room_data.dict()
    name = chat_room_data.pop('name')
    members = chat_room_data.pop('members', [])
    db_repository = SQLAlchemyCRUDRepository(ChatRoom, db_session)
    chat_room = await ChatRoomService(db_repository).create_chat_room(name, members, **chat_room_data)
    db_repository.db_query = select(ChatRoom).options(
        joinedload(ChatRoom.members).load_only(User.id), joinedload(ChatRoom.photos)
    )
    return await db_repository.get_one(ChatRoom.id == chat_room.id)


@router.patch('/chat_rooms/{chat_room_id}', response_model=ChatRoomDetailSchema)
async def update_chat_room_view(
        chat_room_id: int,
        chat_room_data: ChatRoomUpdateSchema,
        request_user: User = Depends(),
        db_session: AsyncSession = Depends(),
):
    await ChatRoomPermission(request_user).check_permissions()
    db_repository = SQLAlchemyCRUDRepository(ChatRoom, db_session, get_chat_rooms_db_query(request_user))
    chat_room = await db_repository.get_one(ChatRoom.id == chat_room_id)
    chat_room_data: dict = chat_room_data.dict(exclude_unset=True)
    members = chat_room_data.pop('members', None)
    if members:
        db_repository.db_query = select(User).where(User.id.in_(members))
        members = await db_repository.get_many()
        db_repository.db_query = None
    return await ChatRoomService(db_repository).update_chat_room(chat_room, members=members, **chat_room_data)
