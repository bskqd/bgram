from fastapi import Header
from sqlalchemy import select
from sqlalchemy.sql import Select

from accounts.models import User
from chat.models import Message
from core.services.authorization import JWTAuthenticationServices


async def get_messages_queryset() -> Select:
    return select(Message)


async def get_request_user(authorization: str = Header(...)) -> User:
    return await JWTAuthenticationServices.validate_authorization_header(authorization)
