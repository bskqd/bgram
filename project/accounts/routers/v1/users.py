from typing import List

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import Select

from accounts.models import User
from accounts.schemas import users as user_schemas
from accounts.services.users import UserService
from chat.models import ChatRoom
from mixins import dependencies as mixins_dependencies
from mixins import views as mixins_views

router = APIRouter()


@cbv(router)
class UserView(mixins_views.AbstractView):
    db_session: Session = Depends(mixins_dependencies.db_session)

    def get_db_query(self) -> Select:
        return select(
            User
        ).where(
            User.id == self.request_user.id
        ).options(
            joinedload(User.chat_rooms).load_only(ChatRoom.id),
            joinedload(User.photos)
        )

    @router.get('/users', response_model=List[user_schemas.UserSchema])
    async def list_users_view(self):
        return await UserService(self.db_session).list_users(self.get_db_query())

    @router.get('/users/{user_id}', response_model=user_schemas.UserSchema)
    async def retrieve_user_view(self, user_id: int):
        return await UserService(self.db_session).retrieve_user(user_id, db_query=self.get_db_query())

    @router.patch('/users/{user_id}', response_model=user_schemas.UserSchema)
    async def update_user_view(self, user_id: int, user_data: user_schemas.UserUpdateSchema):
        user_service = UserService(self.db_session)
        user = await user_service.retrieve_user(user_id, db_query=self.get_db_query())
        return await user_service.update_user(user, **user_data.dict(exclude_unset=True))

    @router.post('/users/{user_id}/upload_file', response_model=user_schemas.UserSchema)
    async def upload_user_photo_view(self, user_id: int, file: UploadFile = File(...)):
        user_service = UserService(self.db_session)
        await user_service.create_user_photo(user_id, file)
        return await user_service.retrieve_user(user_id, db_query=self.get_db_query())
