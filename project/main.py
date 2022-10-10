from typing import Callable

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.staticfiles import StaticFiles

from accounts.api.filters.users import UserFilterSetABC
from accounts.api.pagination.users import UsersPaginatorABC
from accounts.database.repository.authorization import ConfirmationTokenDatabaseRepositoryABC
from accounts.database.repository.users import UsersDatabaseRepositoryABC, UserFilesDatabaseRepositoryABC
from accounts.dependencies.authorization import AuthorizationDependenciesOverrides
from accounts.dependencies.users import UsersDependenciesOverrides
from accounts.models import User
from accounts.services.authorization import ConfirmationTokensCreateServiceABC, ConfirmationTokensConfirmServiceABC
from accounts.services.users import UsersRetrieveServiceABC, UsersCreateUpdateServiceABC, UserFilesServiceABC
from chat.api.filters.messages import MessagesFilterSetABC
from chat.api.pagination.chat_rooms import ChatRoomsPaginatorABC
from chat.api.pagination.messages import MessagesPaginatorABC
from chat.database.repository.chat_rooms import ChatRoomsDatabaseRepositoryABC
from chat.database.repository.messages import MessagesDatabaseRepositoryABC, MessageFilesDatabaseRepositoryABC
from chat.dependencies.chat_rooms import ChatRoomsDependenciesOverrides
from chat.dependencies.messages.dependencies import MessagesDependenciesOverrides
from chat.services.chat_rooms import ChatRoomsRetrieveServiceABC, ChatRoomsCreateUpdateServiceABC
from chat.services.messages import (
    MessagesRetrieveServiceABC, MessageFilesRetrieveServiceABC, MessageFilesServiceABC,
    MessagesCreateUpdateDeleteServiceABC, MessageFilesFilesystemServiceABC,
)
from core.authentication.middlewares import JWTAuthenticationMiddleware
from core.authentication.services.authentication import AuthenticationServiceABC
from core.authentication.services.jwt_authentication import JWTAuthenticationServiceABC
from core.config import SettingsABC
from core.database.base import DatabaseSession
from core.dependencies.dependencies import EventPublisher, EventReceiver, FastapiDependenciesOverrides
from core.dependencies.providers import settings_provider
from core.routers import v1
from core.tasks_scheduling.arq_settings import create_arq_redis_pool
from core.tasks_scheduling.dependencies import TasksScheduler, TaskSchedulerDependenciesOverrides


def create_application(dependency_overrides_factory: Callable, config: SettingsABC) -> FastAPI:
    application = FastAPI()

    application.add_middleware(JWTAuthenticationMiddleware)

    application.mount(f'/{config.MEDIA_URL}', StaticFiles(directory=config.MEDIA_PATH), name='media')

    application.include_router(v1.router, prefix='/api/v1')

    application.dependency_overrides = dependency_overrides_factory(config)

    return application


def fastapi_dependency_overrides_factory(config: SettingsABC) -> dict:
    dependencies_overrides = FastapiDependenciesOverrides(config)
    tasks_scheduler_dependencies_overrides = TaskSchedulerDependenciesOverrides()
    users_dependencies_overrides = UsersDependenciesOverrides
    authorization_dependencies_overrides = AuthorizationDependenciesOverrides
    messages_dependencies_overrides = MessagesDependenciesOverrides
    chat_rooms_dependencies_overrides = ChatRoomsDependenciesOverrides

    return {
        SettingsABC: dependencies_overrides.get_settings,
        AsyncSession: dependencies_overrides.get_db_session,
        AuthenticationServiceABC: dependencies_overrides.get_authentication_service,
        JWTAuthenticationServiceABC: dependencies_overrides.get_jwt_authentication_service,

        User: dependencies_overrides.get_request_user,
        EventPublisher: dependencies_overrides.get_event_publisher,
        EventReceiver: dependencies_overrides.get_event_receiver,

        TasksScheduler: tasks_scheduler_dependencies_overrides.get_tasks_scheduler,

        UsersDatabaseRepositoryABC: users_dependencies_overrides.get_users_db_repository,
        UserFilesDatabaseRepositoryABC: users_dependencies_overrides.get_user_files_db_repository,
        UsersRetrieveServiceABC: users_dependencies_overrides.get_users_retrieve_service,
        UsersCreateUpdateServiceABC: users_dependencies_overrides.get_users_create_update_service,
        UsersPaginatorABC: users_dependencies_overrides.get_users_paginator,
        UserFilterSetABC: users_dependencies_overrides.get_users_filterset,
        UserFilesServiceABC: users_dependencies_overrides.get_user_files_service,

        ConfirmationTokenDatabaseRepositoryABC:
            authorization_dependencies_overrides.get_confirmation_token_db_repository,
        ConfirmationTokensCreateServiceABC: authorization_dependencies_overrides.get_confirmation_token_create_service,
        ConfirmationTokensConfirmServiceABC: (
            authorization_dependencies_overrides.get_confirmation_token_confirm_service
        ),

        MessagesDatabaseRepositoryABC: messages_dependencies_overrides.get_messages_db_repository,
        MessageFilesDatabaseRepositoryABC: messages_dependencies_overrides.get_message_files_db_repository,
        MessagesRetrieveServiceABC: messages_dependencies_overrides.get_messages_retrieve_service,
        MessagesCreateUpdateDeleteServiceABC: messages_dependencies_overrides.get_messages_create_update_delete_service,
        MessageFilesRetrieveServiceABC: messages_dependencies_overrides.get_message_files_retrieve_service,
        MessageFilesServiceABC: messages_dependencies_overrides.get_message_files_service,
        MessagesFilterSetABC: messages_dependencies_overrides.get_messages_filterset,
        MessagesPaginatorABC: messages_dependencies_overrides.get_messages_paginator,
        MessageFilesFilesystemServiceABC: messages_dependencies_overrides.get_message_files_filesystem_service,

        ChatRoomsDatabaseRepositoryABC: chat_rooms_dependencies_overrides.get_chat_rooms_db_repository,
        ChatRoomsRetrieveServiceABC: chat_rooms_dependencies_overrides.get_chat_rooms_retrieve_service,
        ChatRoomsCreateUpdateServiceABC: chat_rooms_dependencies_overrides.get_chat_rooms_create_update_service,
        ChatRoomsPaginatorABC: chat_rooms_dependencies_overrides.get_chat_rooms_paginator,
    }


app = create_application(fastapi_dependency_overrides_factory, settings_provider())


@app.on_event('startup')
async def open_connections():
    app.state.arq_redis_pool = await create_arq_redis_pool()


@app.on_event('shutdown')
async def close_connections():
    DatabaseSession.close_all()
    await app.state.arq_redis_pool.close()
