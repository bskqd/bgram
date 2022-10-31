from chat.api.filters.messages import MessagesFilterSet, MessagesFilterSetABC
from chat.api.pagination.messages import MessagesPaginationDatabaseObjectsRetrieverStrategy, MessagesPaginatorABC
from chat.database.repository.messages import MessageFilesDatabaseRepositoryABC, MessagesDatabaseRepositoryABC
from chat.dependencies.messages.providers import (
    provide_message_files_db_repository,
    provide_message_files_filesystem_service,
    provide_message_files_retrieve_service,
    provide_message_files_service,
    provide_messages_create_update_delete_service,
    provide_messages_db_repository,
    provide_messages_retrieve_service,
)
from chat.services.messages import (
    MessageFilesFilesystemServiceABC,
    MessageFilesRetrieveServiceABC,
    MessageFilesServiceABC,
    MessagesCreateUpdateDeleteServiceABC,
    MessagesRetrieveServiceABC,
)
from core.dependencies.providers import EventPublisher
from core.filters import FilterSet
from core.pagination import DefaultPaginationClass
from core.tasks_scheduling.dependencies import TasksSchedulerABC
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession


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
    async def get_messages_db_repository(db_session: AsyncSession = Depends()) -> MessagesDatabaseRepositoryABC:
        return provide_messages_db_repository(db_session)

    @staticmethod
    async def get_message_files_db_repository(
        db_session: AsyncSession = Depends(),
    ) -> MessageFilesDatabaseRepositoryABC:
        return provide_message_files_db_repository(db_session)

    @staticmethod
    async def get_message_files_retrieve_service(
        db_repository: MessageFilesDatabaseRepositoryABC = Depends(),
    ) -> MessageFilesRetrieveServiceABC:
        return provide_message_files_retrieve_service(db_repository)

    @staticmethod
    async def get_message_files_filesystem_service(
        db_repository: MessageFilesDatabaseRepositoryABC = Depends(),
    ) -> MessageFilesFilesystemServiceABC:
        return provide_message_files_filesystem_service(db_repository)

    @staticmethod
    async def get_message_files_service(
        message_files_filesystem_service: MessageFilesFilesystemServiceABC = Depends(),
        message_files_db_repository: MessageFilesDatabaseRepositoryABC = Depends(),
        event_publisher: EventPublisher = Depends(),
    ) -> MessageFilesServiceABC:
        return provide_message_files_service(
            message_files_filesystem_service,
            message_files_db_repository,
            event_publisher,
        )

    @staticmethod
    async def get_messages_retrieve_service(
        db_repository: MessagesDatabaseRepositoryABC = Depends(),
    ) -> MessagesRetrieveServiceABC:
        return provide_messages_retrieve_service(db_repository)

    @staticmethod
    async def get_messages_create_update_delete_service(
        request: Request,
        db_repository: MessagesDatabaseRepositoryABC = Depends(),
        event_publisher: EventPublisher = Depends(),
        message_files_service: MessageFilesServiceABC = Depends(),
        tasks_scheduler: TasksSchedulerABC = Depends(),
    ) -> MessagesCreateUpdateDeleteServiceABC:
        chat_room_id = int(chat_room_id) if (chat_room_id := request.path_params.get('chat_room_id')) else None
        return provide_messages_create_update_delete_service(
            db_repository,
            event_publisher,
            message_files_service,
            tasks_scheduler=tasks_scheduler,
            chat_room_id=chat_room_id,
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
