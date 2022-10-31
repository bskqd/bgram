from typing import Optional

from chat.database.repository.messages import (
    MessageFilesDatabaseRepository,
    MessageFilesDatabaseRepositoryABC,
    MessagesDatabaseRepository,
    MessagesDatabaseRepositoryABC,
)
from chat.services.messages import (
    MessageFilesFilesystemService,
    MessageFilesFilesystemServiceABC,
    MessageFilesRetrieveService,
    MessageFilesRetrieveServiceABC,
    MessageFilesService,
    MessageFilesServiceABC,
    MessagesCreateUpdateDeleteService,
    MessagesCreateUpdateDeleteServiceABC,
    MessagesRetrieveService,
    MessagesRetrieveServiceABC,
)
from core.dependencies.providers import EventPublisher
from core.tasks_scheduling.dependencies import TasksSchedulerABC
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


def provide_messages_db_repository(db_session: AsyncSession) -> MessagesDatabaseRepositoryABC:
    return MessagesDatabaseRepository(db_session)


def provide_message_files_db_repository(db_session: AsyncSession) -> MessageFilesDatabaseRepositoryABC:
    return MessageFilesDatabaseRepository(db_session)


def provide_message_files_retrieve_service(
    db_repository: MessageFilesDatabaseRepositoryABC,
) -> MessageFilesRetrieveServiceABC:
    return MessageFilesRetrieveService(db_repository)


def provide_message_files_filesystem_service(
    db_repository: MessageFilesDatabaseRepositoryABC,
) -> MessageFilesFilesystemServiceABC:
    return MessageFilesFilesystemService(db_repository)


def provide_message_files_service(
    message_files_filesystem_service: MessageFilesFilesystemServiceABC,
    message_files_db_repository: MessageFilesDatabaseRepositoryABC,
    event_publisher: EventPublisher,
) -> MessageFilesServiceABC:
    return MessageFilesService(message_files_filesystem_service, message_files_db_repository, event_publisher)


def provide_messages_retrieve_service(db_repository: MessagesDatabaseRepositoryABC) -> MessagesRetrieveServiceABC:
    return MessagesRetrieveService(db_repository)


def provide_messages_create_update_delete_service(
    db_repository: MessagesDatabaseRepositoryABC,
    event_publisher: EventPublisher,
    message_files_service: MessageFilesServiceABC,
    tasks_scheduler: Optional[TasksSchedulerABC] = None,
    chat_room_id: Optional[int] = None,
    request: Optional[Request] = None,
) -> MessagesCreateUpdateDeleteServiceABC:
    if not chat_room_id and request:
        chat_room_id = int(chat_room_id) if (chat_room_id := request.path_params.get('chat_room_id')) else None
    return MessagesCreateUpdateDeleteService(
        db_repository,
        chat_room_id,
        event_publisher,
        message_files_service,
        tasks_scheduler,
    )
