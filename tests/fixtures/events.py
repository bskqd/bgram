import pytest
from core.dependencies.providers import EventPublisher

__all__ = ['event_publisher']


class TestsEventPublisher(EventPublisher):
    async def publish(self, *args):
        pass


@pytest.fixture(scope='session', autouse=True)
def event_publisher() -> EventPublisher:
    return TestsEventPublisher()
