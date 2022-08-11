from fastapi import Header, Depends

from accounts.models import User
from core.authentication.services.jwt_authentication import JWTAuthenticationServiceABC


async def get_request_user(
        authorization: str = Header(...),
        jwt_authentication_service: JWTAuthenticationServiceABC = Depends(),
) -> User:
    return await jwt_authentication_service.validate_authorization_header(authorization)
