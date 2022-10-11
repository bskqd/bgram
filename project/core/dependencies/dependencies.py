from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.models import User
from core.authentication.services.authentication import AuthenticationServiceABC
from core.authentication.services.jwt_authentication import JWTAuthenticationService, JWTAuthenticationServiceABC
from core.config import SettingsABC
from core.database.base import DatabaseSession
from core.dependencies.providers import provide_event_publisher, EventPublisher, EventReceiver, provide_event_receiver


class FastapiDependenciesOverrides:
    def __init__(self, config: SettingsABC):
        self.config = config
        self.db_sessionmaker = DatabaseSession

    def override_dependencies(self) -> dict:
        return {
            SettingsABC: self.get_settings,
            AsyncSession: self.get_db_session,
            AuthenticationServiceABC: self.get_authentication_service,
            JWTAuthenticationServiceABC: self.get_jwt_authentication_service,
            User: self.get_request_user,
            EventPublisher: self.get_event_publisher,
            EventReceiver: self.get_event_receiver,
        }

    async def get_db_session(self):
        async with (session := self.db_sessionmaker()):
            yield session

    async def get_settings(self):
        return self.config

    async def get_authentication_service(self):
        return JWTAuthenticationService(self.config)

    async def get_jwt_authentication_service(self):
        return JWTAuthenticationService(self.config)

    @staticmethod
    async def get_request_user(request: Request):
        return request.state.user

    @staticmethod
    async def get_event_publisher() -> EventPublisher:
        return provide_event_publisher()

    @staticmethod
    async def get_event_receiver() -> EventReceiver:
        return provide_event_receiver()
