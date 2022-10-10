from typing import AsyncIterator

from fastapi import Request

from core.authentication.services.jwt_authentication import JWTAuthenticationService
from core.config import SettingsABC
from core.contrib.redis import redis_client
from core.database.base import DatabaseSession


class EventPublisher:
    async def publish(self, *args):
        pass


class EventReceiver:
    async def subscribe(self, *args, **kwargs):
        pass

    async def unsubscribe(self, *args):
        pass

    async def listen(self) -> AsyncIterator:
        pass


class FastapiDependenciesOverrides:
    def __init__(self, config: SettingsABC):
        self.config = config
        self.db_sessionmaker = DatabaseSession

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
        return redis_client

    @staticmethod
    async def get_event_receiver() -> EventReceiver:
        return redis_client.pubsub()
