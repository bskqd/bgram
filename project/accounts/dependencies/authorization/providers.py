from sqlalchemy.ext.asyncio import AsyncSession

from accounts.database.repository.authorization import (
    ConfirmationTokenDatabaseRepositoryABC, ConfirmationTokenDatabaseRepository,
)
from accounts.database.repository.users import UsersDatabaseRepositoryABC
from accounts.services.authorization import (
    EmailConfirmationTokensCreateService, ConfirmationTokensCreateServiceABC, EmailConfirmationTokensConfirmService,
    ConfirmationTokensConfirmServiceABC,
)
from accounts.services.users import UsersCreateUpdateServiceABC
from core.config import SettingsABC


def provide_confirmation_token_db_repository(db_session: AsyncSession) -> ConfirmationTokenDatabaseRepositoryABC:
    return ConfirmationTokenDatabaseRepository(db_session)


def provide_confirmation_token_create_service(
        db_repository: ConfirmationTokenDatabaseRepositoryABC,
) -> ConfirmationTokensCreateServiceABC:
    return EmailConfirmationTokensCreateService(db_repository)


def provide_confirmation_token_confirm_service(
        users_db_repository: UsersDatabaseRepositoryABC,
        users_create_update_service: UsersCreateUpdateServiceABC,
        settings: SettingsABC,
) -> ConfirmationTokensConfirmServiceABC:
    return EmailConfirmationTokensConfirmService(users_db_repository, users_create_update_service, settings)
