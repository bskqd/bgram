from sqlalchemy.ext.asyncio import AsyncSession

from chat.database.repository.chat_rooms import ChatRoomsDatabaseRepositoryABC, ChatRoomsDatabaseRepository
from chat.services.chat_rooms import (
    ChatRoomsRetrieveService, ChatRoomsCreateUpdateService, ChatRoomsRetrieveServiceABC,
    ChatRoomsCreateUpdateServiceABC,
)


def provide_chat_rooms_db_repository(db_session: AsyncSession) -> ChatRoomsDatabaseRepositoryABC:
    return ChatRoomsDatabaseRepository(db_session)


def provide_chat_rooms_retrieve_service(db_repository: ChatRoomsDatabaseRepositoryABC) -> ChatRoomsRetrieveServiceABC:
    return ChatRoomsRetrieveService(db_repository)


def provide_chat_rooms_create_update_service(
        db_repository: ChatRoomsDatabaseRepositoryABC,
) -> ChatRoomsCreateUpdateServiceABC:
    return ChatRoomsCreateUpdateService(db_repository)
