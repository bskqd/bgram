import abc
from datetime import datetime, timedelta

from accounts.models import EmailConfirmationToken, User
from accounts.services.exceptions.authentication import InvalidConfirmationTokenException
from accounts.services.users import UsersCreateUpdateServiceABC
from core.config import SettingsABC
from core.database.repository import BaseDatabaseRepository
from core.dependencies.providers import provide_settings
from sqlalchemy import select


class AuthenticationServiceABC(abc.ABC):
    @classmethod
    @abc.abstractmethod
    async def validate_authorization_header(cls, header: str) -> User:
        pass


class ConfirmationTokensCreateServiceABC(abc.ABC):
    @abc.abstractmethod
    async def create_confirmation_token(self, user: User) -> EmailConfirmationToken:
        pass


class EmailConfirmationTokensCreateService(ConfirmationTokensCreateServiceABC):
    def __init__(self, db_repository: BaseDatabaseRepository):
        self.db_repository = db_repository

    async def create_confirmation_token(self, user: User) -> EmailConfirmationToken:
        token = EmailConfirmationToken(user=user)
        token = await self.db_repository.create_from_object(token)
        await self.db_repository.commit()
        await self.db_repository.refresh(token)
        return token


class ConfirmationTokensConfirmServiceABC(abc.ABC):
    @abc.abstractmethod
    async def confirm_confirmation_token(self, user_id: int, token: str) -> User:
        pass


class EmailConfirmationTokensConfirmService(ConfirmationTokensConfirmServiceABC):
    def __init__(
        self,
        users_db_repository: BaseDatabaseRepository,
        users_update_service: UsersCreateUpdateServiceABC,
        settings: SettingsABC = provide_settings(),
    ):
        self.users_db_repository = users_db_repository
        self.users_update_service = users_update_service
        self.settings = settings

    async def confirm_confirmation_token(self, user_id: int, token: str) -> User:
        token_is_valid_query = (
            select(User)
            .join(
                User.email_confirmation_tokens,
            )
            .where(
                User.id == user_id,
                EmailConfirmationToken.created_at
                >= datetime.now() - timedelta(self.settings.CONFIRMATION_TOKEN_VALID_HOURS),
                EmailConfirmationToken.token == token,
            )
        )
        is_token_valid = await self.users_db_repository.exists(db_query=token_is_valid_query)
        if not is_token_valid:
            raise InvalidConfirmationTokenException
        return await self.users_update_service.update_user(user_id, is_active=True)
