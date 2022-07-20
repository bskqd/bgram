from sqlalchemy.sql import Select

from accounts.models import User
from chat.services.chat_rooms import ChatRoomsRetrieveService
from core.pagination import PaginationDatabaseObjectsRetrieverStrategyABC


class ChatRoomsPaginationDatabaseObjectsRetrieverStrategy(PaginationDatabaseObjectsRetrieverStrategyABC):
    def __init__(self, chat_rooms_service: ChatRoomsRetrieveService):
        self.chat_rooms_service = chat_rooms_service

    async def get_many(self, db_query: Select) -> list[User]:
        return await self.chat_rooms_service.get_many_chat_rooms(db_query=db_query)

    async def count(self, db_query: Select) -> int:
        return await self.chat_rooms_service.count_chat_rooms(db_query=db_query)
