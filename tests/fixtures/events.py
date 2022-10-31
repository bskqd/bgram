import pytest_asyncio
from core.dependencies.providers import EventPublisher, provide_event_publisher

__all__ = ['event_publisher']


@pytest_asyncio.fixture()
def event_publisher() -> EventPublisher:
    return provide_event_publisher()
