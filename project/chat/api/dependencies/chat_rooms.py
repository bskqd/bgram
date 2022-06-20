from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from chat.api.pagination.chat_rooms import ChatRoomsPaginationDatabaseObjectsRetriever
from chat.models import ChatRoom
from chat.services.chat_rooms import ChatRoomRetrieveService, ChatRoomCreateUpdateService
from core.database.repository import SQLAlchemyCRUDRepository, BaseCRUDRepository
from core.pagination import DefaultPaginationClass


async def get_chat_rooms_db_repository(db_session: AsyncSession = Depends()) -> BaseCRUDRepository:
    return SQLAlchemyCRUDRepository(ChatRoom, db_session)


async def get_chat_rooms_retrieve_service(db_repository=Depends(get_chat_rooms_db_repository)):
    return ChatRoomRetrieveService(db_repository)


async def get_chat_rooms_create_update_service(db_repository=Depends(get_chat_rooms_db_repository)):
    return ChatRoomCreateUpdateService(db_repository)


async def get_chat_rooms_paginator(
        request: Request,
        chat_rooms_retrieve_service=Depends(get_chat_rooms_retrieve_service)
) -> DefaultPaginationClass:
    chat_rooms_db_objects_retriever = ChatRoomsPaginationDatabaseObjectsRetriever(chat_rooms_retrieve_service)
    return DefaultPaginationClass(request, chat_rooms_db_objects_retriever)
