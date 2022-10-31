import abc
import uuid
from datetime import datetime, timedelta
from typing import Iterable, Optional

from accounts.models import User
from core.authentication.services.authentication import AuthenticationServiceABC
from core.config import SettingsABC
from core.database.base import provide_db_sessionmaker
from core.dependencies.providers import provide_settings
from fastapi import HTTPException
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.sql.expression import true
from starlette import status


class JWTAuthenticationServiceABC(AuthenticationServiceABC, abc.ABC):
    @staticmethod
    @abc.abstractmethod
    async def create_token(user_id: int, token_type: str) -> str:
        pass

    @classmethod
    @abc.abstractmethod
    async def validate_token(
        cls,
        token: str,
        valid_token_types: Optional[Iterable] = None,
    ) -> User:
        pass


class JWTAuthenticationService(JWTAuthenticationServiceABC):
    """
    Service class for user authentication.
    """

    credentials_exception = HTTPException(
        status_code=401,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    def __init__(self, settings: Optional[SettingsABC] = provide_settings()):
        self.settings = settings
        self.valid_token_types = (settings.JWT_ACCESS_TOKEN_TYPE, settings.JWT_REFRESH_TOKEN_TYPE)

    async def create_token(self, user_id: int, token_type: str) -> str:
        payload = {
            'user_id': user_id,
            'exp': datetime.now() + timedelta(minutes=self.settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
            'token_type': token_type,
            'jti': uuid.uuid4().hex,
        }
        return jwt.encode(payload, self.settings.JWT_SECRET_KEY)

    async def validate_authorization_header(self, header: str) -> User:
        try:
            token_type, token = header.split()
        except ValueError:
            raise self.credentials_exception
        if token_type != self.settings.JWT_TOKEN_TYPE_NAME:
            raise self.credentials_exception
        return await self.validate_token(token)

    async def validate_token(
        self,
        token: str,
        valid_token_types: Optional[Iterable] = None,
    ) -> User:
        valid_token_types = valid_token_types or self.valid_token_types
        try:
            payload = jwt.decode(token, self.settings.JWT_SECRET_KEY, algorithms=[self.settings.JWT_ALGORITHM])
        except JWTError:
            raise self.credentials_exception
        return await self._validate_payload(payload, valid_token_types)

    async def _validate_payload(self, payload: dict, valid_token_types: Iterable) -> User:
        user_id = payload.get('user_id')
        exp = payload.get('exp')
        token_type = payload.get('token_type')
        jti = payload.get('jti')
        if not user_id or not exp or not token_type or not jti:
            raise self.credentials_exception
        try:
            token_expired_at = datetime.utcfromtimestamp(int(exp))
        except TypeError:
            raise self.credentials_exception
        if token_type not in valid_token_types:
            raise self.credentials_exception
        await self._check_token_expiration(token_type, token_expired_at)
        await self._check_jti_is_valid_uuid(jti)
        return await self._get_user(user_id)

    async def _check_token_expiration(self, token_type: str, token_expired_at: datetime):
        current_datetime = datetime.now()
        access_toke_is_expired = (
            token_type == self.settings.JWT_ACCESS_TOKEN_TYPE
            and token_expired_at < current_datetime - timedelta(minutes=self.settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token_is_expired = (
            token_type == self.settings.JWT_REFRESH_TOKEN_TYPE
            and token_expired_at < current_datetime - timedelta(minutes=self.settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
        )
        if access_toke_is_expired or refresh_token_is_expired:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token is expired',
                headers={'WWW-Authenticate': 'Bearer'},
            )

    async def _check_jti_is_valid_uuid(self, jti: str):
        try:
            uuid.UUID(jti)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='"jti" is not a valid uuid',
                headers={'WWW-Authenticate': 'Bearer'},
            )

    async def _get_user(self, user_id: int) -> User:
        async with (db_session := provide_db_sessionmaker()()):
            get_user_query = select(User).where(User.id == user_id, User.is_active == true())
            user = await db_session.scalar(get_user_query)
            if user:
                return user
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='There is no active user found with such user_id.',
                headers={'WWW-Authenticate': 'Bearer'},
            )
