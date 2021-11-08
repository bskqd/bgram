from fastapi import Request, HTTPException, Response
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings
from core.services.authorization import JWTAuthenticationServices


class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for user authentication via JWT token.
    """

    invalid_credentials_response = Response(status_code=401,
                                            content='Could not validate credentials',
                                            headers={'WWW-Authenticate': 'Bearer'})

    async def dispatch(self, request: Request, call_next):
        authorization_header = request.headers.get('Authorization')
        if authorization_header:
            try:
                token_type, token = authorization_header.split()
            except ValueError:
                return self.invalid_credentials_response
            if token_type != settings.JWT_TOKEN_TYPE_NAME:
                return self.invalid_credentials_response
            try:
                request.state.user = await JWTAuthenticationServices.validate_token(token)
            except HTTPException as exception:
                return Response(status_code=exception.status_code, content=exception.detail, headers=exception.headers)
        else:
            request.state.user = None
        return await call_next(request)
