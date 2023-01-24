from fastapi.exceptions import HTTPException
from starlette import status


class InvalidConfirmationTokenException(Exception):
    def __init__(self):
        self.message = 'Confirmation token is not valid or expired'

    def __str__(self):
        return repr(self.message)


class CredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )


class TokenExpiredException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token is expired',
            headers={'WWW-Authenticate': 'Bearer'},
        )


class InvalidJTIException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='"jti" is not a valid uuid',
            headers={'WWW-Authenticate': 'Bearer'},
        )


class InvalidUserIdException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='There is no active user found with such user_id.',
            headers={'WWW-Authenticate': 'Bearer'},
        )


class ConfirmationTokenCreationException(Exception):
    def __init__(self):
        super().__init__('Error during the user confirmation token creation')
