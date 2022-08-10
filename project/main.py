from typing import Callable

from fastapi import FastAPI
from pydantic import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.staticfiles import StaticFiles

from accounts.api.filters.users import UserFilterSetABC
from accounts.api.pagination.users import UsersPaginatorABC
from accounts.database.repository.users import UsersDatabaseRepositoryABC, UserFilesDatabaseRepositoryABC
from accounts.dependencies.users import UsersDependenciesProvider
from accounts.models import User
from accounts.services.users import UsersRetrieveServiceABC, UsersCreateUpdateServiceABC, UserFilesServiceABC
from chat.api.filters.messages import MessagesFilterSetABC
from chat.api.pagination.chat_rooms import ChatRoomsPaginatorABC
from chat.api.pagination.messages import MessagesPaginatorABC
from chat.database.repository.chat_rooms import ChatRoomsDatabaseRepositoryABC
from chat.database.repository.messages import MessagesDatabaseRepositoryABC, MessageFilesDatabaseRepositoryABC
from chat.dependencies.chat_rooms import ChatRoomsDependenciesProvider
from chat.dependencies.messages import MessagesDependenciesProvider
from chat.services.chat_rooms import ChatRoomsRetrieveServiceABC, ChatRoomsCreateUpdateServiceABC
from chat.services.messages import (
    MessagesRetrieveServiceABC, MessageFilesRetrieveServiceABC, MessageFilesServiceABC,
    MessagesCreateUpdateDeleteServiceABC,
)
from core.config import settings
from core.dependencies import EventPublisher, EventReceiver, FastapiDependenciesProvider
from core.middleware.authentication import JWTAuthenticationMiddleware
from core.routers import v1


def create_application(dependency_overrides_factory: Callable, config: BaseSettings) -> FastAPI:
    application = FastAPI()

    application.add_middleware(JWTAuthenticationMiddleware)

    application.mount(f'/{config.MEDIA_URL}', StaticFiles(directory=config.MEDIA_PATH), name='media')

    application.include_router(v1.router, prefix='/api/v1')

    application.dependency_overrides = dependency_overrides_factory(config)

    return application


def fastapi_dependency_overrides_factory(config: BaseSettings) -> dict:
    dependencies_provider = FastapiDependenciesProvider(config)
    users_dependencies_provider = UsersDependenciesProvider
    messages_dependencies_provider = MessagesDependenciesProvider
    chat_rooms_dependencies_provider = ChatRoomsDependenciesProvider

    return {
        AsyncSession: dependencies_provider.get_db_session,
        User: dependencies_provider.get_request_user,
        EventPublisher: dependencies_provider.get_event_publisher,
        EventReceiver: dependencies_provider.get_event_receiver,

        UsersDatabaseRepositoryABC: users_dependencies_provider.get_users_db_repository,
        UserFilesDatabaseRepositoryABC: users_dependencies_provider.get_user_files_db_repository,
        UsersRetrieveServiceABC: users_dependencies_provider.get_users_retrieve_service,
        UsersCreateUpdateServiceABC: users_dependencies_provider.get_users_create_update_service,
        UsersPaginatorABC: users_dependencies_provider.get_users_paginator,
        UserFilterSetABC: users_dependencies_provider.get_users_filterset,
        UserFilesServiceABC: users_dependencies_provider.get_user_files_service,

        MessagesDatabaseRepositoryABC: messages_dependencies_provider.get_messages_db_repository,
        MessageFilesDatabaseRepositoryABC: messages_dependencies_provider.get_message_files_db_repository,
        MessagesRetrieveServiceABC: messages_dependencies_provider.get_messages_retrieve_service,
        MessagesCreateUpdateDeleteServiceABC: messages_dependencies_provider.get_messages_create_update_delete_service,
        MessageFilesRetrieveServiceABC: messages_dependencies_provider.get_message_files_retrieve_service,
        MessageFilesServiceABC: messages_dependencies_provider.get_message_files_service,
        MessagesFilterSetABC: messages_dependencies_provider.get_messages_filterset,
        MessagesPaginatorABC: messages_dependencies_provider.get_messages_paginator,

        ChatRoomsDatabaseRepositoryABC: chat_rooms_dependencies_provider.get_chat_rooms_db_repository,
        ChatRoomsRetrieveServiceABC: chat_rooms_dependencies_provider.get_chat_rooms_retrieve_service,
        ChatRoomsCreateUpdateServiceABC: chat_rooms_dependencies_provider.get_chat_rooms_create_update_service,
        ChatRoomsPaginatorABC: chat_rooms_dependencies_provider.get_chat_rooms_paginator,
    }


app = create_application(fastapi_dependency_overrides_factory, settings)
