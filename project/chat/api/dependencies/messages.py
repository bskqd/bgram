from fastapi import Request, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from chat.api.filters.messages import MessagesFilterSet
from chat.api.pagination.messages import MessagesPaginationDatabaseObjectsRetrieverStrategy
from chat.models import Message, MessagePhoto
from chat.services.messages import MessagesCreateUpdateDeleteService, MessagesRetrieveService, MessageFilesServices, \
    MessageFilesRetrieveService
from core.database.repository import BaseCRUDRepository, SQLAlchemyCRUDRepository
from core.dependencies import EventPublisher
from core.filters import FilterSet
from core.pagination import DefaultPaginationClass
from core.services.files import FilesService


async def get_messages_db_repository(db_session: AsyncSession = Depends()) -> BaseCRUDRepository:
    return SQLAlchemyCRUDRepository(Message, db_session)


async def get_message_files_db_repository(db_session: AsyncSession = Depends()) -> BaseCRUDRepository:
    return SQLAlchemyCRUDRepository(MessagePhoto, db_session)


async def get_messages_retrieve_service(db_repository=Depends(get_messages_db_repository)):
    return MessagesRetrieveService(db_repository)


async def get_file_service_for_message_files(messages_db_repository=Depends(get_messages_db_repository)):
    return FilesService(messages_db_repository, MessagePhoto)


async def get_message_files_retrieve_service(db_repository=Depends(get_message_files_db_repository)):
    return MessageFilesRetrieveService(db_repository)


async def get_message_files_service(
        request: Request,
        message_files_retrieve_service=Depends(get_message_files_retrieve_service),
        files_service=Depends(get_file_service_for_message_files),
        event_publisher: EventPublisher = Depends()
):
    message_file_id = request.path_params.get('message_file_id')
    message_file = await message_files_retrieve_service.get_one_message_file(
        MessagePhoto.id == message_file_id,
        db_query=select(MessagePhoto).options(joinedload(MessagePhoto.message))
    )
    return MessageFilesServices(message_file, files_service, event_publisher)


async def get_messages_create_update_delete_service(
        request: Request,
        db_repository=Depends(get_messages_retrieve_service),
        event_publisher: EventPublisher = Depends(),
        files_service_for_message_files=Depends(get_file_service_for_message_files),
):
    chat_room_id = request.path_params.get('chat_room_id')
    return MessagesCreateUpdateDeleteService(
        db_repository, chat_room_id, event_publisher, files_service_for_message_files,
    )


async def get_messages_filterset(request: Request) -> FilterSet:
    return MessagesFilterSet(request=request)


async def get_messages_paginator(
        request: Request,
        chat_rooms_retrieve_service=Depends(get_messages_retrieve_service)
) -> DefaultPaginationClass:
    messages_db_objects_retriever_strategy = MessagesPaginationDatabaseObjectsRetrieverStrategy(
        chat_rooms_retrieve_service
    )
    return DefaultPaginationClass(request, messages_db_objects_retriever_strategy)
