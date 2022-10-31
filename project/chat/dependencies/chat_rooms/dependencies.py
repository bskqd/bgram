from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from chat.api.pagination.chat_rooms import ChatRoomsPaginationDatabaseObjectsRetrieverStrategy, ChatRoomsPaginatorABC
from chat.database.repository.chat_rooms import ChatRoomsDatabaseRepositoryABC
from chat.dependencies.chat_rooms.providers import (
    provide_chat_rooms_db_repository, provide_chat_rooms_retrieve_service, provide_chat_rooms_create_update_service,
)
from chat.services.chat_rooms import ChatRoomsRetrieveServiceABC, ChatRoomsCreateUpdateServiceABC
from core.pagination import DefaultPaginationClass


class ChatRoomsDependenciesOverrides:
    @classmethod
    def override_dependencies(cls) -> dict:
        return {
            ChatRoomsDatabaseRepositoryABC: cls.get_chat_rooms_db_repository,
            ChatRoomsRetrieveServiceABC: cls.get_chat_rooms_retrieve_service,
            ChatRoomsCreateUpdateServiceABC: cls.get_chat_rooms_create_update_service,
            ChatRoomsPaginatorABC: cls.get_chat_rooms_paginator,
        }

    @staticmethod
    async def get_chat_rooms_db_repository(db_session: AsyncSession = Depends()) -> ChatRoomsDatabaseRepositoryABC:
        return provide_chat_rooms_db_repository(db_session)

    @staticmethod
    async def get_chat_rooms_retrieve_service(
            db_repository: ChatRoomsDatabaseRepositoryABC = Depends(),
    ) -> ChatRoomsRetrieveServiceABC:
        return provide_chat_rooms_retrieve_service(db_repository)

    @staticmethod
    async def get_chat_rooms_create_update_service(
            db_repository: ChatRoomsDatabaseRepositoryABC = Depends(),
    ) -> ChatRoomsCreateUpdateServiceABC:
        return provide_chat_rooms_create_update_service(db_repository)

    @staticmethod
    async def get_chat_rooms_paginator(
            request: Request,
            chat_rooms_retrieve_service: ChatRoomsRetrieveServiceABC = Depends(),
    ) -> DefaultPaginationClass:
        chat_rooms_db_objects_retriever_strategy = ChatRoomsPaginationDatabaseObjectsRetrieverStrategy(
            chat_rooms_retrieve_service,
        )
        return DefaultPaginationClass(request, chat_rooms_db_objects_retriever_strategy)
