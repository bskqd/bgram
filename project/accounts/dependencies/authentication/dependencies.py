from accounts.database.repository.authentication import ConfirmationTokenDatabaseRepositoryABC
from accounts.database.repository.users import UsersDatabaseRepositoryABC
from accounts.dependencies.authentication.providers import (
    provide_authentication_service,
    provide_confirmation_token_confirm_service,
    provide_confirmation_token_create_service,
    provide_confirmation_token_db_repository,
    provide_jwt_authentication_service,
)
from accounts.models import User
from accounts.services.authentication.authentication import (
    AuthenticationServiceABC,
    ConfirmationTokensConfirmServiceABC,
    ConfirmationTokensCreateServiceABC,
)
from accounts.services.authentication.jwt_authentication import JWTAuthenticationServiceABC
from accounts.services.users import UsersCreateUpdateServiceABC, UsersRetrieveServiceABC
from core.config import SettingsABC
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession


class AuthorizationDependenciesOverrides:
    @classmethod
    def override_dependencies(cls) -> dict:
        return {
            AuthenticationServiceABC: cls.get_authentication_service,
            JWTAuthenticationServiceABC: cls.get_jwt_authentication_service,
            User: cls.get_request_user,
            ConfirmationTokenDatabaseRepositoryABC: cls.get_confirmation_token_db_repository,
            ConfirmationTokensCreateServiceABC: cls.get_confirmation_token_create_service,
            ConfirmationTokensConfirmServiceABC: cls.get_confirmation_token_confirm_service,
        }

    @staticmethod
    async def get_authentication_service(
        settings: SettingsABC = Depends(),
        users_retrieve_service: UsersRetrieveServiceABC = Depends(),
    ) -> AuthenticationServiceABC:
        return provide_authentication_service(settings, users_retrieve_service)

    @staticmethod
    async def get_jwt_authentication_service(
        settings: SettingsABC = Depends(),
        users_retrieve_service: UsersRetrieveServiceABC = Depends(),
    ) -> JWTAuthenticationServiceABC:
        return provide_jwt_authentication_service(settings, users_retrieve_service)

    @staticmethod
    async def get_request_user(
        authorization: str = Header(...),
        authentication_service: AuthenticationServiceABC = Depends(),
    ) -> User:
        return await authentication_service.validate_authorization_header(header=authorization)

    @staticmethod
    async def get_confirmation_token_db_repository(
        db_session: AsyncSession = Depends(),
    ) -> ConfirmationTokenDatabaseRepositoryABC:
        return provide_confirmation_token_db_repository(db_session)

    @staticmethod
    async def get_confirmation_token_create_service(
        db_repository: ConfirmationTokenDatabaseRepositoryABC = Depends(),
    ) -> ConfirmationTokensCreateServiceABC:
        return provide_confirmation_token_create_service(db_repository)

    @staticmethod
    async def get_confirmation_token_confirm_service(
        users_db_repository: UsersDatabaseRepositoryABC = Depends(),
        users_create_update_service: UsersCreateUpdateServiceABC = Depends(),
        settings: SettingsABC = Depends(),
    ) -> ConfirmationTokensConfirmServiceABC:
        return provide_confirmation_token_confirm_service(users_db_repository, users_create_update_service, settings)
