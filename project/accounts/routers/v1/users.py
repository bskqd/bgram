from typing import List

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select

from accounts.models import User
from accounts.schemas import users as user_schemas
from accounts.services.users import UserService
from chat.models import ChatRoom, chatroom_members_association_table
from database.repository import SQLAlchemyCRUDRepository
from mixins import dependencies as mixins_dependencies
from mixins import views as mixins_views

router = APIRouter()


@cbv(router)
class UserView(mixins_views.AbstractView):
    db_session: AsyncSession = Depends(mixins_dependencies.db_session)

    def get_db_query(self) -> Select:
        return select(
            User
        ).join(
            chatroom_members_association_table
        ).options(
            joinedload(User.chat_rooms).load_only(ChatRoom.id), joinedload(User.photos)
        ).where(
            chatroom_members_association_table.c.user_id == self.request_user.id
        )

    @router.get('/users', response_model=List[user_schemas.UserSchema])
    async def list_users_view(self):
        return await SQLAlchemyCRUDRepository(User, self.db_session, self.get_db_query()).get_many()

    @router.get('/users/{user_id}', response_model=user_schemas.UserSchema)
    async def retrieve_user_view(self, user_id: int):
        return await SQLAlchemyCRUDRepository(User, self.db_session, self.get_db_query()).get_one(User.id == user_id)

    @router.patch('/users/{user_id}', response_model=user_schemas.UserSchema)
    async def update_user_view(self, user_id: int, user_data: user_schemas.UserUpdateSchema):
        db_repository = SQLAlchemyCRUDRepository(User, self.db_session, self.get_db_query())
        user = await db_repository.get_one(User.id == user_id)
        return await UserService(db_repository).update_user(user, **user_data.dict(exclude_unset=True))

    @router.post('/users/{user_id}/upload_file', response_model=user_schemas.UserSchema)
    async def upload_user_photo_view(self, user_id: int, file: UploadFile = File(...)):
        db_repository = SQLAlchemyCRUDRepository(User, self.db_session, self.get_db_query())
        await UserService(db_repository).create_user_photo(user_id, file)
        db_repository.db_query = self.get_db_query()
        return await db_repository.get_one(User.id == user_id)
