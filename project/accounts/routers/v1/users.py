from typing import List

from fastapi import APIRouter, UploadFile, File
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select

from accounts.filters.users import UsersFilterSet
from accounts.models import User, UserPhoto
from accounts.schemas import users as user_schemas
from accounts.services.users import UserService
from chat.models import ChatRoom, chatroom_members_association_table
from database.repository import SQLAlchemyCRUDRepository
from mixins import views as mixins_views
from mixins.services.files import FilesService

router = APIRouter()


@cbv(router)
class UserView(mixins_views.AbstractView):
    filterset_class = UsersFilterSet

    def get_db_query(self) -> Select:
        return select(
            User
        ).join(
            chatroom_members_association_table
        ).options(
            joinedload(User.chat_rooms).load_only(ChatRoom.id), joinedload(User.photos)
        ).where(
            chatroom_members_association_table.c.user_id == self.request_user.id,
        )

    @router.get('/users', response_model=List[user_schemas.UserSchema])
    async def list_users_view(self):
        db_repository = SQLAlchemyCRUDRepository(User, self.db_session)
        return await UserService(db_repository).list_users(db_query=self.filter_db_query(self.get_db_query()))

    @router.get('/users/{user_id}', response_model=user_schemas.UserSchema)
    async def retrieve_user_view(self, user_id: int):
        db_repository = SQLAlchemyCRUDRepository(User, self.db_session)
        return await UserService(db_repository).retrieve_user(User.id == user_id, db_query=self.get_db_query())

    @router.patch('/users/{user_id}', response_model=user_schemas.UserSchema)
    async def update_user_view(self, user_id: int, user_data: user_schemas.UserUpdateSchema):
        db_repository = SQLAlchemyCRUDRepository(User, self.db_session)
        user_service = UserService(db_repository)
        user = await user_service.retrieve_user(User.id == user_id, db_query=self.get_db_query())
        return await UserService(db_repository).update_user(user, **user_data.dict(exclude_unset=True))

    @router.post('/users/{user_id}/upload_file', response_model=user_schemas.UserSchema)
    async def upload_user_photo_view(self, user_id: int, file: UploadFile = File(...)):
        db_repository = SQLAlchemyCRUDRepository(User, self.db_session)
        await FilesService(self.db_repository, UserPhoto).create_object_file(file, user_id=user_id)
        return await UserService(db_repository).retrieve_user(User.id == user_id, db_query=self.get_db_query())
