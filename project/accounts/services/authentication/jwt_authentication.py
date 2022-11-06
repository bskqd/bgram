import abc
import uuid
from datetime import datetime, timedelta
from typing import Iterable, Optional

from accounts.models import User
from accounts.services.authentication.authentication import AuthenticationServiceABC
from accounts.services.exceptions.authentication import (
    CredentialsException,
    InvalidJTIException,
    InvalidUserIdException,
    TokenExpiredException,
)
from accounts.services.users import UsersRetrieveServiceABC
from core.config import SettingsABC
from core.dependencies.providers import provide_settings
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import load_only
from sqlalchemy.sql.expression import true


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
    def __init__(
        self,
        users_retrieve_service: UsersRetrieveServiceABC,
        settings: Optional[SettingsABC] = provide_settings(),
    ):
        self.settings = settings
        self.users_retrieve_service = users_retrieve_service
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
            raise CredentialsException
        if token_type != self.settings.JWT_TOKEN_TYPE_NAME:
            raise CredentialsException
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
            raise CredentialsException
        return await self._validate_payload(payload, valid_token_types)

    async def _validate_payload(self, payload: dict, valid_token_types: Iterable) -> User:
        user_id = payload.get('user_id')
        exp = payload.get('exp')
        token_type = payload.get('token_type')
        jti = payload.get('jti')
        if not user_id or not exp or not token_type or not jti:
            raise CredentialsException
        try:
            token_expired_at = datetime.utcfromtimestamp(int(exp))
        except TypeError:
            raise CredentialsException
        if token_type not in valid_token_types:
            raise CredentialsException
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
            raise TokenExpiredException

    async def _check_jti_is_valid_uuid(self, jti: str):
        try:
            uuid.UUID(jti)
        except ValueError:
            raise InvalidJTIException

    async def _get_user(self, user_id: int) -> User:
        user = await self.users_retrieve_service.get_one_user(
            db_query=select(User).options(load_only(User.id)).where(User.id == user_id, User.is_active == true()),
        )
        if user:
            return user
        raise InvalidUserIdException
