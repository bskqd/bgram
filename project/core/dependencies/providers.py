import functools
from typing import AsyncIterator

from core.config import Settings, SettingsABC
from core.contrib.redis import RedisClientProvider


@functools.lru_cache(maxsize=1)
def provide_settings() -> SettingsABC:
    return Settings()


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


def provide_event_publisher() -> EventPublisher:
    return RedisClientProvider.provide_redis_client()


def provide_event_receiver() -> EventReceiver:
    return RedisClientProvider.provide_redis_client().pubsub()
