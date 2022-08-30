from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.database.repository.authorization import ConfirmationTokenDatabaseRepositoryABC
from accounts.models import EmailConfirmationToken
from accounts.services.authorization import EmailConfirmationTokensService
from core.database.repository import SQLAlchemyDatabaseRepository


class AuthorizationDependenciesProvider:
    @staticmethod
    async def get_confirmation_token_db_repository(db_session: AsyncSession = Depends()):
        return SQLAlchemyDatabaseRepository(EmailConfirmationToken, db_session)

    @staticmethod
    async def get_confirmation_token_service(db_repository: ConfirmationTokenDatabaseRepositoryABC = Depends()):
        return EmailConfirmationTokensService(db_repository)
