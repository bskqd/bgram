from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession

from chat.models import Message, MessageFile
from core.database.repository import BaseDatabaseRepository, SQLAlchemyDatabaseRepository


class MessagesDatabaseRepositoryABC(BaseDatabaseRepository, ABC):
    pass


class MessagesDatabaseRepository(SQLAlchemyDatabaseRepository, MessagesDatabaseRepositoryABC):
    def __init__(self, db_session: AsyncSession):
        super().__init__(model=Message, db_session=db_session)


class MessageFilesDatabaseRepositoryABC(BaseDatabaseRepository, ABC):
    pass


class MessageFilesDatabaseRepository(SQLAlchemyDatabaseRepository, MessageFilesDatabaseRepositoryABC):
    def __init__(self, db_session: AsyncSession):
        super().__init__(model=MessageFile, db_session=db_session)
