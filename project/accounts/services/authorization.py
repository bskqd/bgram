from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from accounts.models import User, EmailConfirmationToken
from mixins import utils as mixins_utils, dependencies as mixins_dependencies


async def create_email_confirmation_token(user: User, db_session: Session) -> EmailConfirmationToken:
    token = EmailConfirmationToken(user=user)
    await mixins_utils.create_object_in_database(user, db_session)
    return token
