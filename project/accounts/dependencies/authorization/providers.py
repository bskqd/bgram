from accounts.database.repository.authorization import (
    ConfirmationTokenDatabaseRepository,
    ConfirmationTokenDatabaseRepositoryABC,
)
from accounts.database.repository.users import UsersDatabaseRepositoryABC
from accounts.services.authorization import (
    ConfirmationTokensConfirmServiceABC,
    ConfirmationTokensCreateServiceABC,
    EmailConfirmationTokensConfirmService,
    EmailConfirmationTokensCreateService,
)
from accounts.services.users import UsersCreateUpdateServiceABC
from core.config import SettingsABC
from sqlalchemy.ext.asyncio import AsyncSession


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
