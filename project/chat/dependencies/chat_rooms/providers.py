from accounts.services.users import UsersRetrieveServiceABC
from chat.database.repository.chat_rooms import ChatRoomsDatabaseRepository, ChatRoomsDatabaseRepositoryABC
from chat.services.chat_rooms import (
    ChatRoomsCreateUpdateService,
    ChatRoomsCreateUpdateServiceABC,
    ChatRoomsRetrieveService,
    ChatRoomsRetrieveServiceABC,
)
from sqlalchemy.ext.asyncio import AsyncSession


def provide_chat_rooms_db_repository(db_session: AsyncSession) -> ChatRoomsDatabaseRepositoryABC:
    return ChatRoomsDatabaseRepository(db_session)


def provide_chat_rooms_retrieve_service(db_repository: ChatRoomsDatabaseRepositoryABC) -> ChatRoomsRetrieveServiceABC:
    return ChatRoomsRetrieveService(db_repository)


def provide_chat_rooms_create_update_service(
    db_repository: ChatRoomsDatabaseRepositoryABC,
    chat_rooms_retrieve_service: ChatRoomsRetrieveServiceABC,
    users_retrieve_service: UsersRetrieveServiceABC,
) -> ChatRoomsCreateUpdateServiceABC:
    return ChatRoomsCreateUpdateService(db_repository, chat_rooms_retrieve_service, users_retrieve_service)
