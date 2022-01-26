import uuid
from datetime import datetime, timedelta
from typing import Optional, Iterable

from fastapi import HTTPException
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.sql.expression import true
from starlette import status

from accounts.models import User
from core.config import settings
from database import DatabaseSession

VALID_TOKEN_TYPES = frozenset([settings.JWT_ACCESS_TOKEN_TYPE, settings.JWT_REFRESH_TOKEN_TYPE])


class JWTAuthenticationServices:
    """
    Service class for user authentication.
    """

    credentials_exception = HTTPException(
        status_code=401,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )

    @staticmethod
    async def create_token(user_id: int, token_type: str) -> str:
        payload = {
            'user_id': user_id,
            'exp': datetime.now() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
            'token_type': token_type,
            'jti': uuid.uuid4().hex
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY)

    @classmethod
    async def validate_authorization_header(cls, header: str) -> User:
        try:
            token_type, token = header.split()
        except ValueError:
            raise cls.credentials_exception
        if token_type != settings.JWT_TOKEN_TYPE_NAME:
            raise cls.credentials_exception
        return await cls.validate_token(token)

    @classmethod
    async def validate_token(
            cls,
            token: str,
            valid_token_types: Optional[Iterable] = VALID_TOKEN_TYPES
    ) -> User:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except JWTError:
            raise cls.credentials_exception
        return await cls._validate_payload(payload, valid_token_types)

    @classmethod
    async def _validate_payload(cls, payload: dict, valid_token_types: Iterable) -> User:
        user_id = payload.get('user_id')
        exp = payload.get('exp')
        token_type = payload.get('token_type')
        jti = payload.get('jti')
        if not user_id or not exp or not token_type or not jti:
            raise cls.credentials_exception
        try:
            token_expired_at = datetime.utcfromtimestamp(int(exp))
        except TypeError:
            raise cls.credentials_exception
        if token_type not in valid_token_types:
            raise cls.credentials_exception
        await cls._check_token_expiration(token_type, token_expired_at)
        await cls._check_jti_is_valid_uuid(jti)
        return await cls._get_user(user_id)

    @staticmethod
    async def _check_token_expiration(token_type: str, token_expired_at: datetime):
        current_datetime = datetime.now()
        access_toke_is_expired = (
            token_type == settings.JWT_ACCESS_TOKEN_TYPE and
            token_expired_at < current_datetime - timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token_is_expired = (
            token_type == settings.JWT_REFRESH_TOKEN_TYPE and
            token_expired_at < current_datetime - timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
        )
        if access_toke_is_expired or refresh_token_is_expired:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token is expired',
                headers={'WWW-Authenticate': 'Bearer'},
            )

    @staticmethod
    async def _check_jti_is_valid_uuid(jti: str):
        try:
            uuid.UUID(jti)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='"jti" is not a valid uuid',
                headers={'WWW-Authenticate': 'Bearer'},
            )

    @staticmethod
    async def _get_user(user_id: int) -> User:
        async with (db_session := DatabaseSession()):
            get_user_query = select(User).where(User.id == user_id, User.is_active == true())
            user = await db_session.scalar(get_user_query)
            if user:
                return user
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='There is no active user found with such user_id.',
                headers={'WWW-Authenticate': 'Bearer'},
            )
