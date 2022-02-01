import binascii
import os

from sqlalchemy.orm import Session

from accounts.models import User, EmailConfirmationToken
from mixins.services import crud as mixins_crud_services


def generate_token() -> str:
    return binascii.hexlify(os.urandom(40)).decode()


async def create_email_confirmation_token(user: User, db_session: Session) -> EmailConfirmationToken:
    token = EmailConfirmationToken(user=user)
    await mixins_crud_services.CRUDOperationsService(db_session).create_object_in_database(token)
    return token
