from sqlalchemy import select
from sqlalchemy.orm import joinedload

from chat.constants.messages import MessagesTypeEnum
from chat.dependencies.messages.providers import provide_messages_db_repository, \
    provide_messages_create_update_delete_service, provide_message_files_service, provide_message_files_db_repository, \
    provide_message_files_filesystem_service, provide_messages_retrieve_service
from chat.models import Message

from core.database.base import DatabaseSession
from core.dependencies.providers import provide_event_publisher


# TODO: fix
async def send_scheduled_message(job_context: dict, scheduled_message_id: int):
    async with (db_session := DatabaseSession()):
        messages_db_repository = provide_messages_db_repository(db_session)
        message_files_db_repository = provide_message_files_db_repository(db_session)
        message_files_filesystem_service = provide_message_files_filesystem_service(message_files_db_repository)
        event_publisher = provide_event_publisher()
        message_files_service = provide_message_files_service(
            message_files_filesystem_service, message_files_db_repository, event_publisher,
        )
        messages_retrieve_service = provide_messages_retrieve_service(messages_db_repository)
        messages_update_service = provide_messages_create_update_delete_service(
            messages_db_repository, event_publisher, message_files_service,
        )
        message = await messages_retrieve_service.get_one_message(
            db_query=select(Message).options(joinedload('*')).where(Message.id == scheduled_message_id),
        )
        await messages_update_service.update_message(
            message, mark_as_edited=False, message_type=MessagesTypeEnum.PRIMARY.value,
        )
