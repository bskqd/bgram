from typing import AsyncIterator

from core.config import Settings, SettingsABC
from core.contrib.redis import redis_client


def provide_settings() -> SettingsABC:
    _settings = getattr(provide_settings, '_settings', None)
    if not _settings:
        _settings = Settings()
        setattr(provide_settings, '_settings', _settings)
    return _settings


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
    return redis_client


def provide_event_receiver() -> EventReceiver:
    return redis_client.pubsub()
