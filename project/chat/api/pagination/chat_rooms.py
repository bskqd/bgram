import abc

from accounts.models import User
from chat.services.chat_rooms import ChatRoomsRetrieveServiceABC
from core.pagination import PaginationClassABC, PaginationDatabaseObjectsRetrieverStrategyABC
from sqlalchemy.sql import Select


class ChatRoomsPaginatorABC(PaginationClassABC, abc.ABC):
    pass


class ChatRoomsPaginationDatabaseObjectsRetrieverStrategy(PaginationDatabaseObjectsRetrieverStrategyABC):
    def __init__(self, chat_rooms_service: ChatRoomsRetrieveServiceABC):
        self.chat_rooms_service = chat_rooms_service

    async def get_many(self, db_query: Select) -> list[User]:
        return await self.chat_rooms_service.get_many_chat_rooms(db_query=db_query)

    async def count(self, db_query: Select) -> int:
        return await self.chat_rooms_service.count_chat_rooms(db_query=db_query)
