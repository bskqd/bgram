from accounts.models import User
from accounts.services.authentication.authentication import AuthenticationServiceABC
from fastapi import Depends, Header


async def get_request_user(
    authorization: str = Header(...),
    jwt_authentication_service: AuthenticationServiceABC = Depends(),
) -> User:
    return await jwt_authentication_service.validate_authorization_header(authorization)
