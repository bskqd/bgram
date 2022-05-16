from typing import List

from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select

from accounts.api.v1.schemas import users as user_schemas
from accounts.api.dependencies.users import get_users_filterset
from accounts.models import User, UserPhoto
from accounts.services.users import UserService
from chat.models import chatroom_members_association_table, ChatRoom
from core.database.repository import SQLAlchemyCRUDRepository
from core.services.files import FilesService

router = APIRouter()


def get_users_db_query(request_user: User) -> Select:
    return select(
        User
    ).join(
        chatroom_members_association_table
    ).options(
        joinedload(User.chat_rooms).load_only(ChatRoom.id), joinedload(User.photos)
    ).where(
        chatroom_members_association_table.c.user_id == request_user.id,
    )


@router.get('/users', response_model=List[user_schemas.UserSchema])
async def list_users_view(
        db_session: AsyncSession = Depends(),
        request_user: User = Depends(),
        filterset=Depends(get_users_filterset),
):
    db_repository = SQLAlchemyCRUDRepository(User, db_session)
    return await UserService(db_repository).list_users(
        db_query=filterset.filter_db_query(db_query=get_users_db_query(request_user))
    )


@router.get('/users/{user_id}', response_model=user_schemas.UserSchema)
async def retrieve_user_view(
        user_id: int,
        db_session: AsyncSession = Depends(),
        request_user: User = Depends(),
):
    db_repository = SQLAlchemyCRUDRepository(User, db_session)
    return await UserService(db_repository).retrieve_user(User.id == user_id, db_query=get_users_db_query(request_user))


@router.patch('/users/{user_id}', response_model=user_schemas.UserSchema)
async def update_user_view(
        user_id: int,
        user_data: user_schemas.UserUpdateSchema,
        db_session: AsyncSession = Depends(),
        request_user: User = Depends(),
):
    db_repository = SQLAlchemyCRUDRepository(User, db_session)
    user_service = UserService(db_repository)
    user = await user_service.retrieve_user(User.id == user_id, db_query=get_users_db_query(request_user))
    return await UserService(db_repository).update_user(user, **user_data.dict(exclude_unset=True))


@router.post('/users/{user_id}/upload_file', response_model=user_schemas.UserSchema)
async def upload_user_photo_view(
        user_id: int,
        file: UploadFile = File(...),
        db_session: AsyncSession = Depends(),
        request_user: User = Depends(),
):
    db_repository = SQLAlchemyCRUDRepository(User, db_session)
    await FilesService(db_repository, UserPhoto).create_object_file(file, user_id=user_id)
    return await UserService(db_repository).retrieve_user(User.id == user_id, db_query=get_users_db_query(request_user))
