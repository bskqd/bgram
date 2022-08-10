from abc import ABC

from core.database.repository import BaseDatabaseRepository


class UsersDatabaseRepositoryABC(BaseDatabaseRepository, ABC):
    pass


class UserFilesDatabaseRepositoryABC(BaseDatabaseRepository, ABC):
    pass
