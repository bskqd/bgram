import abc

from accounts.models import User, EmailConfirmationToken
from core.database.repository import BaseDatabaseRepository


class ConfirmationTokensServiceABC(abc.ABC):
    @abc.abstractmethod
    async def create_confirmation_token(self, user: User) -> EmailConfirmationToken:
        pass


class EmailConfirmationTokensService:
    def __init__(self, db_repository: BaseDatabaseRepository):
        self.db_repository = db_repository

    async def create_confirmation_token(self, user: User) -> EmailConfirmationToken:
        token = EmailConfirmationToken(user=user)
        token = await self.db_repository.create(token)
        await self.db_repository.commit()
        await self.db_repository.refresh(token)
        return token
