from chat.constants.messages import MessagesTypeEnum
from chat.database.selectors.messages import get_message_db_query
from chat.dependencies.messages.providers import (
    provide_messages_db_repository, provide_messages_create_update_delete_service, provide_message_files_service,
    provide_message_files_db_repository, provide_message_files_filesystem_service, provide_messages_retrieve_service,
)
from chat.models import Message
from core.database.base import provide_db_sessionmaker
from core.dependencies.providers import provide_event_publisher


async def send_scheduled_message(job_context: dict, scheduled_message_id: int):
    async with (db_session := provide_db_sessionmaker()()):
        messages_db_repository = provide_messages_db_repository(db_session)
        messages_retrieve_service = provide_messages_retrieve_service(messages_db_repository)
        message = await messages_retrieve_service.get_one_message(
            db_query=get_message_db_query().where(Message.id == scheduled_message_id),
        )
        if not message:
            return
        message_files_db_repository = provide_message_files_db_repository(db_session)
        message_files_filesystem_service = provide_message_files_filesystem_service(message_files_db_repository)
        event_publisher = provide_event_publisher()
        message_files_service = provide_message_files_service(
            message_files_filesystem_service, message_files_db_repository, event_publisher,
        )
        messages_update_service = provide_messages_create_update_delete_service(
            messages_db_repository, event_publisher, message_files_service,
        )
        await messages_update_service.update_message(
            message, mark_as_edited=False, message_type=MessagesTypeEnum.PRIMARY.value,
        )
