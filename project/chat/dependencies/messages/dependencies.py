from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from chat.api.filters.messages import MessagesFilterSet, MessagesFilterSetABC
from chat.api.pagination.messages import MessagesPaginationDatabaseObjectsRetrieverStrategy, MessagesPaginatorABC
from chat.database.repository.messages import MessagesDatabaseRepositoryABC, MessageFilesDatabaseRepositoryABC
from chat.models import Message, MessageFile
from chat.services.messages import (
    MessagesCreateUpdateDeleteService, MessagesRetrieveService, MessageFilesService, MessageFilesRetrieveService,
    MessagesRetrieveServiceABC, MessageFilesServiceABC, MessageFilesFilesystemService,
    MessageFilesFilesystemServiceABC, MessagesCreateUpdateDeleteServiceABC, MessageFilesRetrieveServiceABC,
)
from core.database.repository import BaseDatabaseRepository, SQLAlchemyDatabaseRepository
from core.dependencies.dependencies import EventPublisher
from core.filters import FilterSet
from core.pagination import DefaultPaginationClass
from core.tasks_scheduling.dependencies import TasksScheduler


class MessagesDependenciesOverrides:
    @classmethod
    def override_dependencies(cls) -> dict:
        return {
            MessagesDatabaseRepositoryABC: cls.get_messages_db_repository,
            MessageFilesDatabaseRepositoryABC: cls.get_message_files_db_repository,
            MessagesRetrieveServiceABC: cls.get_messages_retrieve_service,
            MessagesCreateUpdateDeleteServiceABC: cls.get_messages_create_update_delete_service,
            MessageFilesRetrieveServiceABC: cls.get_message_files_retrieve_service,
            MessageFilesServiceABC: cls.get_message_files_service,
            MessagesFilterSetABC: cls.get_messages_filterset,
            MessagesPaginatorABC: cls.get_messages_paginator,
            MessageFilesFilesystemServiceABC: cls.get_message_files_filesystem_service,
        }

    @staticmethod
    async def get_messages_db_repository(db_session: AsyncSession = Depends()) -> BaseDatabaseRepository:
        return SQLAlchemyDatabaseRepository(Message, db_session)

    @staticmethod
    async def get_message_files_db_repository(db_session: AsyncSession = Depends()) -> BaseDatabaseRepository:
        return SQLAlchemyDatabaseRepository(MessageFile, db_session)

    @staticmethod
    async def get_messages_retrieve_service(db_repository: MessagesDatabaseRepositoryABC = Depends()):
        return MessagesRetrieveService(db_repository)

    @staticmethod
    async def get_message_files_retrieve_service(db_repository: MessageFilesDatabaseRepositoryABC = Depends()):
        return MessageFilesRetrieveService(db_repository)

    @staticmethod
    async def get_message_files_filesystem_service(db_repository: MessageFilesDatabaseRepositoryABC = Depends()):
        return MessageFilesFilesystemService(db_repository)

    @staticmethod
    async def get_message_files_service(
            message_files_filesystem_service: MessageFilesFilesystemServiceABC = Depends(),
            message_files_db_repository: MessageFilesDatabaseRepositoryABC = Depends(),
            event_publisher: EventPublisher = Depends(),
    ):
        return MessageFilesService(message_files_filesystem_service, message_files_db_repository, event_publisher)

    @staticmethod
    async def get_messages_create_update_delete_service(
            request: Request,
            db_repository: MessagesDatabaseRepositoryABC = Depends(),
            event_publisher: EventPublisher = Depends(),
            message_files_service: MessageFilesServiceABC = Depends(),
            tasks_scheduler: TasksScheduler = Depends(),
    ):
        chat_room_id = int(chat_room_id) if (chat_room_id := request.path_params.get('chat_room_id')) else None
        return MessagesCreateUpdateDeleteService(
            db_repository, chat_room_id, event_publisher, message_files_service, tasks_scheduler,
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
