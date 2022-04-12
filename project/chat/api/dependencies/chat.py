from fastapi import Header

from accounts.models import User
from core.services.authorization import JWTAuthenticationServices


async def get_request_user(authorization: str = Header(...)) -> User:
    return await JWTAuthenticationServices.validate_authorization_header(authorization)
