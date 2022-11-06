from core.config import SettingsABC
from core.database.base import provide_db_sessionmaker
from core.dependencies.providers import EventPublisher, EventReceiver, provide_event_publisher, provide_event_receiver
from sqlalchemy.ext.asyncio import AsyncSession


class FastapiDependenciesOverrides:
    def __init__(self, config: SettingsABC):
        self.config = config
        self.db_sessionmaker = provide_db_sessionmaker()

    def override_dependencies(self) -> dict:
        return {
            SettingsABC: self.get_settings,
            AsyncSession: self.get_db_session,
            EventPublisher: self.get_event_publisher,
            EventReceiver: self.get_event_receiver,
        }

    async def get_db_session(self) -> AsyncSession:
        async with (session := self.db_sessionmaker()):
            yield session

    async def get_settings(self) -> SettingsABC:
        return self.config

    @staticmethod
    async def get_event_publisher() -> EventPublisher:
        return provide_event_publisher()

    @staticmethod
    async def get_event_receiver() -> EventReceiver:
        return provide_event_receiver()
