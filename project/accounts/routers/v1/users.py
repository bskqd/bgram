from typing import List

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi_utils.cbv import cbv
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from accounts.dependencies import users as user_dependencies
from accounts.schemas import users as user_schemas
from accounts.services.users import UserService
from mixins import dependencies as mixins_dependencies
from mixins import views as mixins_views

router = APIRouter()


@cbv(router)
class UserView(mixins_views.AbstractView):
    queryset: Select = Depends(user_dependencies.get_users_queryset)
    db_session: Session = Depends(mixins_dependencies.db_session)

    @router.get('/users', response_model=List[user_schemas.UserSchema])
    async def list_users_view(self):
        return await UserService(self.db_session).list_users(self.queryset)

    @router.get('/users/{user_id}', response_model=user_schemas.UserSchema)
    async def retrieve_user_view(self, user_id: int):
        return await UserService(self.db_session).retrieve_user(user_id, queryset=self.queryset)

    @router.patch('/users/{user_id}', response_model=user_schemas.UserSchema)
    async def update_user_view(self, user_id: int, user_data: user_schemas.UserUpdateSchema):
        user_service = UserService(self.db_session)
        user = await user_service.retrieve_user(user_id, queryset=self.queryset)
        return await user_service.update_user(user, **user_data.dict(exclude_unset=True))

    @router.post('/users/{user_id}/upload_file', response_model=user_schemas.UserSchema)
    async def upload_user_photo_view(self, user_id: int, file: UploadFile = File(...)):
        user_service = UserService(self.db_session)
        await user_service.create_user_photo(user_id, file)
        return await user_service.retrieve_user(user_id, queryset=self.queryset)
