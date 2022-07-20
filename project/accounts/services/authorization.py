from sqlalchemy.ext.asyncio import AsyncSession

from accounts.models import User, EmailConfirmationToken
from core.database.repository import SQLAlchemyDatabaseRepository


async def create_email_confirmation_token(user: User, db_session: AsyncSession) -> EmailConfirmationToken:
    token = EmailConfirmationToken(user=user)
    return await SQLAlchemyDatabaseRepository(EmailConfirmationToken, db_session).create(token)
