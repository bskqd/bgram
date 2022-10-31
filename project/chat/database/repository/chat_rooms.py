from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession

from chat.models import ChatRoom
from core.database.repository import BaseDatabaseRepository, SQLAlchemyDatabaseRepository


class ChatRoomsDatabaseRepositoryABC(BaseDatabaseRepository, ABC):
    pass


class ChatRoomsDatabaseRepository(SQLAlchemyDatabaseRepository, ChatRoomsDatabaseRepositoryABC):
    def __init__(self, db_session: AsyncSession):
        super().__init__(model=ChatRoom, db_session=db_session)
