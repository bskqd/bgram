from abc import ABC

from sqlalchemy.sql import Select

from accounts.models import User
from accounts.services.users import UsersRetrieveServiceABC
from core.pagination import PaginationDatabaseObjectsRetrieverStrategyABC, PaginationClassABC


class UsersPaginatorABC(PaginationClassABC, ABC):
    pass


class UsersPaginationDatabaseObjectsRetrieverStrategy(PaginationDatabaseObjectsRetrieverStrategyABC):
    def __init__(self, users_service: UsersRetrieveServiceABC):
        self.users_retrieve_service = users_service

    async def get_many(self, db_query: Select) -> list[User]:
        return await self.users_retrieve_service.get_many_users(db_query=db_query)

    async def count(self, db_query: Select) -> int:
        return await self.users_retrieve_service.count_users(db_query=db_query)
