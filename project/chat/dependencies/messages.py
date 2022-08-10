from fastapi import Request, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from chat.api.filters.messages import MessagesFilterSet
from chat.api.pagination.messages import MessagesPaginationDatabaseObjectsRetrieverStrategy
from chat.database.repository.messages import MessagesDatabaseRepositoryABC, MessageFilesDatabaseRepositoryABC
from chat.models import Message, MessagePhoto
from chat.services.messages import (
    MessagesCreateUpdateDeleteService, MessagesRetrieveService, MessageFilesService, MessageFilesRetrieveService,
    MessageFilesRetrieveServiceABC, MessagesRetrieveServiceABC, MessageFilesServiceABC,
)
from core.database.repository import BaseDatabaseRepository, SQLAlchemyDatabaseRepository
from core.dependencies import EventPublisher
from core.filters import FilterSet
from core.pagination import DefaultPaginationClass


class MessagesDependenciesProvider:
    @staticmethod
    async def get_messages_db_repository(db_session: AsyncSession = Depends()) -> BaseDatabaseRepository:
        return SQLAlchemyDatabaseRepository(Message, db_session)

    @staticmethod
    async def get_message_files_db_repository(db_session: AsyncSession = Depends()) -> BaseDatabaseRepository:
        return SQLAlchemyDatabaseRepository(MessagePhoto, db_session)

    @staticmethod
    async def get_messages_retrieve_service(db_repository: MessagesDatabaseRepositoryABC = Depends()):
        return MessagesRetrieveService(db_repository)

    @staticmethod
    async def get_message_files_retrieve_service(db_repository: MessageFilesDatabaseRepositoryABC = Depends()):
        return MessageFilesRetrieveService(db_repository)

    @staticmethod
    async def get_message_files_service(
            request: Request,
            message_files_db_repository: MessageFilesDatabaseRepositoryABC = Depends(),
            message_files_retrieve_service: MessageFilesRetrieveServiceABC = Depends(),
            event_publisher: EventPublisher = Depends(),
    ):
        message_file_id = request.path_params.get('message_file_id')
        message_file = await message_files_retrieve_service.get_one_message_file(
            MessagePhoto.id == message_file_id,
            db_query=select(MessagePhoto).options(joinedload(MessagePhoto.message)),
        )
        return MessageFilesService(message_files_db_repository, message_file, event_publisher)

    @staticmethod
    async def get_messages_create_update_delete_service(
            request: Request,
            db_repository: MessagesDatabaseRepositoryABC = Depends(),
            event_publisher: EventPublisher = Depends(),
            message_files_service: MessageFilesServiceABC = Depends(),
    ):
        chat_room_id = request.path_params.get('chat_room_id')
        return MessagesCreateUpdateDeleteService(
            db_repository, chat_room_id, event_publisher, message_files_service,
        )

    @staticmethod
    async def get_messages_filterset(request: Request) -> FilterSet:
        return MessagesFilterSet(request=request)

    @staticmethod
    async def get_messages_paginator(
            request: Request,
            messages_retrieve_service: MessagesRetrieveServiceABC = Depends(),
    ) -> DefaultPaginationClass:
        messages_db_objects_retriever_strategy = MessagesPaginationDatabaseObjectsRetrieverStrategy(
            messages_retrieve_service,
        )
        return DefaultPaginationClass(request, messages_db_objects_retriever_strategy)
