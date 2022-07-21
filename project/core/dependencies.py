from fastapi import Request
from pydantic import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.contrib.redis import redis_client


class EventPublisher:
    def publish(self, *args):
        pass


class EventReceiver:
    def subscribe(self, *args, **kwargs):
        pass

    def unsubscribe(self, *args):
        pass

    def listen(self):
        pass


class FastapiDependenciesProvider:
    def __init__(self, config: BaseSettings):
        self.db_sessionmaker = sessionmaker(
            create_async_engine(config.DATABASE_URL),
            autoflush=False,
            class_=AsyncSession,
        )

    async def get_db_session(self):
        async with (session := self.db_sessionmaker()):
            yield session

    @staticmethod
    async def get_request_user(request: Request):
        return request.state.user

    @staticmethod
    async def get_event_publisher():
        return redis_client

    @staticmethod
    async def get_event_receiver():
        return redis_client.pubsub()
