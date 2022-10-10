from fastapi import Request, HTTPException, Response
from starlette.middleware.base import BaseHTTPMiddleware

from core.authentication.services.jwt_authentication import JWTAuthenticationService


class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for user authentication via JWT token.
    """

    invalid_credentials_response = Response(
        status_code=401,
        content='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    async def dispatch(self, request: Request, call_next):
        authorization_header = request.headers.get('Authorization')
        if authorization_header:
            try:
                request.state.user = await JWTAuthenticationService().validate_authorization_header(
                    authorization_header,
                )
            except HTTPException as exception:
                return Response(status_code=exception.status_code, content=exception.detail, headers=exception.headers)
        else:
            request.state.user = None
        return await call_next(request)
