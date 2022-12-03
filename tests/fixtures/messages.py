from typing import Optional

import pytest
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
    'create_message',
]


@pytest.fixture()
def messages_db_repository(db_session) -> MessagesDatabaseRepositoryABC:
    return provide_messages_db_repository(db_session)


@pytest.fixture()
def message_files_db_repository(db_session) -> MessageFilesDatabaseRepositoryABC:
    return provide_message_files_db_repository(db_session)


@pytest.fixture()
def message_files_filesystem_service(message_files_db_repository) -> MessageFilesFilesystemServiceABC:
    return provide_message_files_filesystem_service(message_files_db_repository)


@pytest.fixture()
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


@pytest.fixture()
def messages_create_update_delete_service(
    messages_db_repository,
    event_publisher,
    tasks_scheduler,
    message_files_service,
) -> MessagesCreateUpdateDeleteServiceABC:
    return provide_messages_create_update_delete_service(
        messages_db_repository,
        event_publisher,
        message_files_service,
        tasks_scheduler=tasks_scheduler,
    )


@pytest_asyncio.fixture()
async def create_message(messages_db_repository):
    async def _create_message(_returning_options: Optional[tuple] = None, **kwargs):
        return await messages_db_repository.create(_returning_options=_returning_options, **kwargs)

    return _create_message
