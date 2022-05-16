from typing import Optional

from aioredis import Redis
from aioredis.client import PubSub
from fastapi import Request

from accounts.models import User
from core.contrib.redis import redis_client
from core.database.base import DatabaseSession
from core.pagination import DefaultPaginationClass


class EventPublisher:
    pass


class EventReceiver:
    pass


async def db_session() -> DatabaseSession:
    async with (session := DatabaseSession()):
        yield session


async def get_request_user(request: Request) -> Optional[User]:
    return request.state.user


async def get_event_publisher() -> Redis:
    return redis_client


async def get_event_receiver() -> PubSub:
    return redis_client.pubsub()


async def get_paginator(request: Request) -> DefaultPaginationClass:
    return DefaultPaginationClass(request=request)
