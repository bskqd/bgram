from typing import List

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi_utils.cbv import cbv
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from accounts.crud import user as user_crud
from accounts.dependencies import user as user_dependencies
from accounts.schemas import user as user_schemas
from mixins import dependencies as mixins_dependencies
from mixins import views as mixins_views

router = APIRouter()


@cbv(router)
class UserView(mixins_views.AbstractView):
    available_db_data: Select = Depends(user_dependencies.available_db_data)
    db_session: Session = Depends(mixins_dependencies.db_session)

    @router.get('/users', response_model=List[user_schemas.UserSchema])
    async def list_users_view(self):
        return await user_crud.get_users(self.db_session, self.available_db_data)

    @router.get('/users/{user_id}', response_model=user_schemas.UserSchema)
    async def retrieve_user_view(self, user_id: int):
        return await user_crud.get_user(user_id, self.db_session, available_db_data=self.available_db_data)

    @router.patch('/users/{user_id}', response_model=user_schemas.UserSchema)
    async def update_user_view(self, user_id: int, user_data: user_schemas.UserUpdateSchema):
        user = await user_crud.get_user(user_id, available_db_data=self.available_db_data, db_session=self.db_session)
        return await user_crud.update_user(user, self.db_session, **user_data.dict(exclude_unset=True))

    @router.post('/users/{user_id}/upload_file', response_model=user_schemas.UserSchema)
    async def upload_user_photo_view(self, user_id: int, file: UploadFile = File(...)):
        await user_crud.create_user_photo(user_id, file, db_session=self.db_session)
        return await user_crud.get_user(user_id, self.db_session, available_db_data=self.available_db_data)
