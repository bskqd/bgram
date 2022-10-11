from typing import Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from chat.database.repository.messages import MessagesDatabaseRepositoryABC, MessageFilesDatabaseRepositoryABC
from chat.models import Message, MessageFile
from chat.services.messages import (
    MessagesRetrieveService, MessageFilesFilesystemService,
    MessageFilesFilesystemServiceABC, MessagesCreateUpdateDeleteService, MessageFilesServiceABC, MessageFilesService,
    MessagesRetrieveServiceABC, MessagesCreateUpdateDeleteServiceABC, MessageFilesRetrieveService,
    MessageFilesRetrieveServiceABC,
)
from core.database.repository import SQLAlchemyDatabaseRepository
from core.dependencies.dependencies import EventPublisher
from core.tasks_scheduling.dependencies import TasksScheduler


async def messages_db_repository_provider(db_session: AsyncSession) -> MessagesDatabaseRepositoryABC:
    return SQLAlchemyDatabaseRepository(Message, db_session)


async def message_files_db_repository_provider(db_session: AsyncSession) -> MessageFilesDatabaseRepositoryABC:
    return SQLAlchemyDatabaseRepository(MessageFile, db_session)


async def messages_retrieve_service_provider(
        db_repository: MessagesDatabaseRepositoryABC,
) -> MessagesRetrieveServiceABC:
    return MessagesRetrieveService(db_repository)


async def message_files_retrieve_service_provider(
        db_repository: MessageFilesDatabaseRepositoryABC,
) -> MessageFilesRetrieveServiceABC:
    return MessageFilesRetrieveService(db_repository)


async def message_files_filesystem_service_provider(
        db_repository: MessageFilesDatabaseRepositoryABC,
) -> MessageFilesFilesystemServiceABC:
    return MessageFilesFilesystemService(db_repository)


async def message_files_service_provider(
        message_files_filesystem_service: MessageFilesFilesystemServiceABC,
        message_files_db_repository: MessageFilesDatabaseRepositoryABC,
        event_publisher: EventPublisher,
) -> MessageFilesServiceABC:
    return MessageFilesService(message_files_filesystem_service, message_files_db_repository, event_publisher)


async def messages_create_update_delete_service_provider(
        db_repository: MessagesDatabaseRepositoryABC,
        event_publisher: EventPublisher,
        message_files_service: MessageFilesServiceABC,
        tasks_scheduler: TasksScheduler,
        chat_room_id: Optional[int] = None,
        request: Optional[Request] = None,
) -> MessagesCreateUpdateDeleteServiceABC:
    if not chat_room_id and request:
        chat_room_id = int(chat_room_id) if (chat_room_id := request.path_params.get('chat_room_id')) else None
    return MessagesCreateUpdateDeleteService(
        db_repository, chat_room_id, event_publisher, message_files_service, tasks_scheduler,
    )
