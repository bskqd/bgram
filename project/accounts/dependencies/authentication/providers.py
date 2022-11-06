from accounts.database.repository.authentication import (
    ConfirmationTokenDatabaseRepository,
    ConfirmationTokenDatabaseRepositoryABC,
)
from accounts.database.repository.users import UsersDatabaseRepositoryABC
from accounts.services.authentication.authentication import (
    AuthenticationServiceABC,
    ConfirmationTokensConfirmServiceABC,
    ConfirmationTokensCreateServiceABC,
    EmailConfirmationTokensConfirmService,
    EmailConfirmationTokensCreateService,
)
from accounts.services.authentication.jwt_authentication import JWTAuthenticationService, JWTAuthenticationServiceABC
from accounts.services.users import UsersCreateUpdateServiceABC, UsersRetrieveServiceABC
from core.config import SettingsABC
from sqlalchemy.ext.asyncio import AsyncSession


def provide_authentication_service(
    settings: SettingsABC,
    users_retrieve_service: UsersRetrieveServiceABC,
) -> AuthenticationServiceABC:
    return JWTAuthenticationService(users_retrieve_service, settings)


def provide_jwt_authentication_service(
    settings: SettingsABC,
    users_retrieve_service: UsersRetrieveServiceABC,
) -> JWTAuthenticationServiceABC:
    return JWTAuthenticationService(users_retrieve_service, settings)


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
