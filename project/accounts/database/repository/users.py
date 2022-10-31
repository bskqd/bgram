from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession

from accounts.models import User, UserFile
from core.database.repository import BaseDatabaseRepository, SQLAlchemyDatabaseRepository


class UsersDatabaseRepositoryABC(BaseDatabaseRepository, ABC):
    pass


class UsersDatabaseRepository(SQLAlchemyDatabaseRepository, UsersDatabaseRepositoryABC):
    def __init__(self, db_session: AsyncSession):
        super().__init__(model=User, db_session=db_session)


class UserFilesDatabaseRepositoryABC(BaseDatabaseRepository, ABC):
    pass


class UserFilesDatabaseRepository(SQLAlchemyDatabaseRepository, UserFilesDatabaseRepositoryABC):
    def __init__(self, db_session: AsyncSession):
        super().__init__(model=UserFile, db_session=db_session)
