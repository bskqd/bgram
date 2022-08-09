import abc
from typing import Optional

from sqlalchemy.sql import Select

from accounts.models import User
from accounts.utils.users import hash_password
from core.database.repository import BaseDatabaseRepository
from core.services.files import FilesServiceABC, FilesService


class UsersRetrieveServiceABC(abc.ABC):
    @abc.abstractmethod
    async def get_one_user(self, *args, db_query: Optional[Select] = None) -> User:
        pass

    @abc.abstractmethod
    async def get_many_users(self, *args, db_query: Optional[Select] = None) -> list[User]:
        pass

    @abc.abstractmethod
    async def count_users(self, *args, db_query: Optional[Select] = None) -> int:
        pass


class UsersRetrieveService(UsersRetrieveServiceABC):
    def __init__(self, db_repository: BaseDatabaseRepository):
        self.db_repository = db_repository

    async def get_one_user(self, *args, db_query: Optional[Select] = None) -> User:
        if db_query is not None:
            self.db_repository.db_query = db_query
        return await self.db_repository.get_one(*args)

    async def get_many_users(self, *args, db_query: Optional[Select] = None) -> list[User]:
        if db_query is not None:
            self.db_repository.db_query = db_query
        return await self.db_repository.get_many(*args)

    async def count_users(self, *args, db_query: Optional[Select] = None) -> int:
        if db_query is not None:
            self.db_repository.db_query = db_query
        return await self.db_repository.count(*args)


class UsersCreateUpdateServiceABC(abc.ABC):
    @abc.abstractmethod
    async def create_user(self, *args, **kwargs) -> User:
        pass

    @abc.abstractmethod
    async def update_user(self, user: User, **data_for_update) -> User:
        pass


class UsersCreateUpdateService(UsersCreateUpdateServiceABC):
    def __init__(self, db_repository: BaseDatabaseRepository):
        self.db_repository = db_repository

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


class UserFilesServiceABC(FilesServiceABC, abc.ABC):
    pass


class UserFilesService(UserFilesServiceABC, FilesService):
    file_model = User
