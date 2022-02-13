from typing import List

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from accounts.models import User, UserPhoto
from accounts.utils.users import get_hashed_password
from mixins.services import crud as mixins_crud_services, files as mixins_files_services


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, nickname: str, email: str, password: str, **kwargs) -> User:
        user = User(nickname=nickname, email=email, password=get_hashed_password(password), **kwargs)
        await mixins_crud_services.CRUDOperationsService(self.db_session).create_object_in_database(user)
        return user

    async def list_users(self, db_query: Select = select(User)) -> List[User]:
        users = await self.db_session.scalars(db_query)
        return users.unique().all()

    async def retrieve_user(self, search_value: int, lookup_kwarg: str = 'id', db_query: Select = select(User)) -> User:
        return await mixins_crud_services.CRUDOperationsService(self.db_session).get_object(
            db_query, User, search_value, lookup_kwarg=lookup_kwarg
        )

    async def update_user(self, user: User, **data_for_update) -> User:
        return await mixins_crud_services.CRUDOperationsService(self.db_session).update_object_in_database(
            user, **data_for_update
        )

    async def create_user_photo(self, user_id: int, file: UploadFile) -> UserPhoto:
        return await mixins_files_services.FilesService(self.db_session).create_object_file(
            UserPhoto, file, user_id=user_id
        )
