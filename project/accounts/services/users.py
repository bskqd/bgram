import abc
from typing import Optional

from accounts.models import User
from core.config import SettingsABC
from core.database.repository import BaseDatabaseRepository
from core.services.files import FilesService, FilesServiceABC
from sqlalchemy.sql import Select


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
        return await self.db_repository.get_one(*args, db_query=db_query)

    async def get_many_users(self, *args, db_query: Optional[Select] = None) -> list[User]:
        return await self.db_repository.get_many(*args, db_query=db_query)

    async def count_users(self, *args, db_query: Optional[Select] = None) -> int:
        return await self.db_repository.count(*args, db_query=db_query)


class UsersCreateUpdateServiceABC(abc.ABC):
    @abc.abstractmethod
    async def create_user(self, *args, **kwargs) -> User:
        pass

    @abc.abstractmethod
    async def update_user(self, user_id: int, _returning_options: Optional[tuple] = None, **data_for_update) -> User:
        pass


class UsersCreateUpdateService(UsersCreateUpdateServiceABC):
    def __init__(self, db_repository: BaseDatabaseRepository, settings: SettingsABC):
        self.db_repository = db_repository
        self.settings = settings

    async def create_user(self, nickname: str, email: str, password: str, **kwargs) -> User:
        user = User(nickname=nickname, email=email, password=self._hash_password(password), **kwargs)
        await self.db_repository.create(user)
        await self.db_repository.commit()
        await self.db_repository.refresh(user)
        return user

    async def update_user(self, user_id: int, _returning_options: Optional[tuple] = None, **data_for_update) -> User:
        password = data_for_update.pop('password', None)
        if password:
            data_for_update['password'] = self._hash_password(password)
        user = await self.db_repository.update(
            User.id == user_id,
            **data_for_update,
            _returning_options=_returning_options,
        )
        await self.db_repository.commit()
        await self.db_repository.refresh(user)
        return user

    def _hash_password(self, plain_text_password: str) -> str:
        return self.settings.PWD_CONTEXT.hash(plain_text_password)


class UserFilesServiceABC(FilesServiceABC, abc.ABC):
    pass


class UserFilesService(FilesService, UserFilesServiceABC):
    file_model = User
