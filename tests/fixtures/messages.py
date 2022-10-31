import pytest_asyncio
from chat.database.repository.messages import MessageFilesDatabaseRepositoryABC, MessagesDatabaseRepositoryABC
from chat.dependencies.messages.providers import (
    provide_message_files_db_repository,
    provide_message_files_filesystem_service,
    provide_message_files_service,
    provide_messages_create_update_delete_service,
    provide_messages_db_repository,
)
from chat.services.messages import (
    MessageFilesFilesystemServiceABC,
    MessageFilesServiceABC,
    MessagesCreateUpdateDeleteServiceABC,
)

__all__ = [
    'messages_db_repository',
    'message_files_db_repository',
    'message_files_filesystem_service',
    'message_files_service',
    'messages_create_update_delete_service',
]


@pytest_asyncio.fixture()
def messages_db_repository(db_session) -> MessagesDatabaseRepositoryABC:
    return provide_messages_db_repository(db_session)


@pytest_asyncio.fixture()
def message_files_db_repository(db_session) -> MessageFilesDatabaseRepositoryABC:
    return provide_message_files_db_repository(db_session)


@pytest_asyncio.fixture()
def message_files_filesystem_service(message_files_db_repository) -> MessageFilesFilesystemServiceABC:
    return provide_message_files_filesystem_service(message_files_db_repository)


@pytest_asyncio.fixture()
def message_files_service(
    message_files_filesystem_service,
    message_files_db_repository,
    event_publisher,
) -> MessageFilesServiceABC:
    return provide_message_files_service(
        message_files_filesystem_service,
        message_files_db_repository,
        event_publisher,
    )


@pytest_asyncio.fixture()
def messages_create_update_delete_service(
    messages_db_repository,
    event_publisher,
    message_files_service,
) -> MessagesCreateUpdateDeleteServiceABC:
    return provide_messages_create_update_delete_service(
        messages_db_repository,
        event_publisher,
        message_files_service,
    )
