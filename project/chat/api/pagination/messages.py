from sqlalchemy.sql import Select

from accounts.models import User
from chat.services.messages import MessagesRetrieveService
from core.pagination import PaginationDatabaseObjectsRetrieverStrategyABC


class MessagesPaginationDatabaseObjectsRetrieverStrategy(PaginationDatabaseObjectsRetrieverStrategyABC):
    def __init__(self, messages_service: MessagesRetrieveService):
        self.messages_service = messages_service

    async def get_many(self, db_query: Select) -> list[User]:
        return await self.messages_service.get_many_messages(db_query=db_query)

    async def count(self, db_query: Select) -> int:
        return await self.messages_service.count_messages(db_query=db_query)
