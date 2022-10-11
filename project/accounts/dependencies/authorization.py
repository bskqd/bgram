from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.database.repository.authorization import ConfirmationTokenDatabaseRepositoryABC
from accounts.database.repository.users import UsersDatabaseRepositoryABC
from accounts.models import EmailConfirmationToken
from accounts.services.authorization import (
    EmailConfirmationTokensCreateService, EmailConfirmationTokensConfirmService,
    ConfirmationTokensCreateServiceABC, ConfirmationTokensConfirmServiceABC,
)
from accounts.services.users import UsersCreateUpdateServiceABC
from core.config import SettingsABC
from core.database.repository import SQLAlchemyDatabaseRepository


class AuthorizationDependenciesOverrides:
    @classmethod
    def override_dependencies(cls) -> dict:
        return {
            ConfirmationTokenDatabaseRepositoryABC: cls.get_confirmation_token_db_repository,
            ConfirmationTokensCreateServiceABC: cls.get_confirmation_token_create_service,
            ConfirmationTokensConfirmServiceABC: cls.get_confirmation_token_confirm_service,
        }

    @staticmethod
    async def get_confirmation_token_db_repository(db_session: AsyncSession = Depends()):
        return SQLAlchemyDatabaseRepository(EmailConfirmationToken, db_session)

    @staticmethod
    async def get_confirmation_token_create_service(db_repository: ConfirmationTokenDatabaseRepositoryABC = Depends()):
        return EmailConfirmationTokensCreateService(db_repository)

    @staticmethod
    async def get_confirmation_token_confirm_service(
            users_db_repository: UsersDatabaseRepositoryABC = Depends(),
            users_create_update_service: UsersCreateUpdateServiceABC = Depends(),
            settings: SettingsABC = Depends(),
    ):
        return EmailConfirmationTokensConfirmService(users_db_repository, users_create_update_service, settings)
