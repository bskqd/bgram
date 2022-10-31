from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession

from accounts.models.authorization import EmailConfirmationToken
from core.database.repository import BaseDatabaseRepository, SQLAlchemyDatabaseRepository


class ConfirmationTokenDatabaseRepositoryABC(BaseDatabaseRepository, ABC):
    pass


class ConfirmationTokenDatabaseRepository(SQLAlchemyDatabaseRepository, ConfirmationTokenDatabaseRepositoryABC):
    def __init__(self, db_session: AsyncSession):
        super().__init__(model=EmailConfirmationToken, db_session=db_session)
