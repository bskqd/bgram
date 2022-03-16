from typing import Optional

from sqlalchemy.sql import Select

from accounts.models import User
from accounts.utils.users import hash_password
from database.repository import BaseCRUDRepository


class UserService:
    def __init__(self, db_repository: BaseCRUDRepository):
        self.db_repository = db_repository

    async def retrieve_user(self, *args, db_query: Optional[Select] = None) -> User:
        if db_query is not None:
            self.db_repository.db_query = db_query
        return await self.db_repository.get_one(*args)

    async def list_users(self, *args, db_query: Optional[Select] = None) -> User:
        if db_query is not None:
            self.db_repository.db_query = db_query
        return await self.db_repository.get_many(*args)

    async def create_user(self, nickname: str, email: str, password: str, **kwargs) -> User:
        user = User(nickname=nickname, email=email, password=hash_password(password), **kwargs)
        await self.db_repository.create(user)
        await self.db_repository.commit()
        await self.db_repository.refresh(user)
        return user

    async def update_user(self, user: User, **data_for_update) -> User:
        user = await self.db_repository.update_object(user, **data_for_update)
        await self.db_repository.commit()
        await self.db_repository.refresh(user)
        return user
