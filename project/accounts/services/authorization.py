import abc
from datetime import datetime, timedelta

from sqlalchemy import select

from accounts.models import User, EmailConfirmationToken
from accounts.services.exceptions.authorization import InvalidConfirmationTokenException
from accounts.services.users import UsersCreateUpdateServiceABC
from core.config import settings
from core.database.repository import BaseDatabaseRepository


class ConfirmationTokensCreateServiceABC(abc.ABC):
    @abc.abstractmethod
    async def create_confirmation_token(self, user: User) -> EmailConfirmationToken:
        pass


class EmailConfirmationTokensCreateService:
    def __init__(self, db_repository: BaseDatabaseRepository):
        self.db_repository = db_repository

    async def create_confirmation_token(self, user: User) -> EmailConfirmationToken:
        token = EmailConfirmationToken(user=user)
        token = await self.db_repository.create(token)
        await self.db_repository.commit()
        await self.db_repository.refresh(token)
        return token


class ConfirmationTokensConfirmServiceABC(abc.ABC):
    @abc.abstractmethod
    async def confirm_confirmation_token(self, user: User, token: str):
        pass


class EmailConfirmationTokensConfirmService:
    def __init__(self, users_db_repository: BaseDatabaseRepository, users_update_service: UsersCreateUpdateServiceABC):
        self.users_db_repository = users_db_repository
        self.users_update_service = users_update_service

    async def confirm_confirmation_token(self, user: User, token: str):
        token_is_valid_query = select(User).join(
            User.email_confirmation_tokens,
        ).where(
            User.id == user.id,
            EmailConfirmationToken.created_at >= datetime.now() - timedelta(settings.CONFIRMATION_TOKEN_VALID_HOURS),
            EmailConfirmationToken.token == token,
        )
        is_token_valid = await self.users_db_repository.exists(db_query=token_is_valid_query)
        if not is_token_valid:
            raise InvalidConfirmationTokenException
        await self.users_update_service.update_user(user, is_active=True)
        await self.users_db_repository.commit()
        await self.users_db_repository.refresh(user)
