from typing import Callable

from fastapi import FastAPI
from pydantic import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.staticfiles import StaticFiles

from accounts.api.filters.users import UserFilterSetABC
from accounts.api.pagination.users import UsersPaginatorABC
from accounts.database.repository.users import UsersDatabaseRepositoryABC
from accounts.dependencies.users import UsersDependenciesProvider
from accounts.models import User
from accounts.services.users import UsersRetrieveServiceABC, UsersCreateUpdateServiceABC, UserFilesServiceABC
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

    return {
        AsyncSession: dependencies_provider.get_db_session,
        User: dependencies_provider.get_request_user,
        EventPublisher: dependencies_provider.get_event_publisher,
        EventReceiver: dependencies_provider.get_event_receiver,
        UsersDatabaseRepositoryABC: users_dependencies_provider.get_users_db_repository,
        UsersRetrieveServiceABC: users_dependencies_provider.get_users_retrieve_service,
        UsersCreateUpdateServiceABC: users_dependencies_provider.get_users_create_update_service,
        UsersPaginatorABC: users_dependencies_provider.get_users_paginator,
        UserFilterSetABC: users_dependencies_provider.get_users_filterset,
        UserFilesServiceABC: users_dependencies_provider.get_user_files_service,
    }


app = create_application(fastapi_dependency_overrides_factory, settings)
