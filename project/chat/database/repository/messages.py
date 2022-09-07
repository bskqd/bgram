from abc import ABC

from core.database.repository import BaseDatabaseRepository


class MessagesDatabaseRepositoryABC(BaseDatabaseRepository, ABC):
    pass


class MessageFilesDatabaseRepositoryABC(BaseDatabaseRepository, ABC):
    pass


class ScheduledMessagesDatabaseRepositoryABC(BaseDatabaseRepository, ABC):
    pass


class ScheduledMessageFilesDatabaseRepositoryABC(BaseDatabaseRepository, ABC):
    pass
