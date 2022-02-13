from sqlalchemy.ext.asyncio import AsyncSession

from accounts.models import User, EmailConfirmationToken
from mixins.services import crud as mixins_crud_services


async def create_email_confirmation_token(user: User, db_session: AsyncSession) -> EmailConfirmationToken:
    token = EmailConfirmationToken(user=user)
    await mixins_crud_services.CRUDOperationsService(db_session).create_object_in_database(token)
    return token
