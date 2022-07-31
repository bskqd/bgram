from typing import Callable

from fastapi import FastAPI
from pydantic import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.staticfiles import StaticFiles

from accounts.api.dependencies.users import UsersDependenciesProvider
from accounts.api.filters.users import IUserFilterSet
from accounts.api.pagination.users import IUsersPaginator
from accounts.database.repository.users import IUsersDatabaseRepository
from accounts.models import User
from accounts.services.users import IUsersRetrieveService, IUsersCreateUpdateService, UserPhotoService
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
        IUsersDatabaseRepository: users_dependencies_provider.get_users_db_repository,
        IUsersRetrieveService: users_dependencies_provider.get_users_retrieve_service,
        IUsersCreateUpdateService: users_dependencies_provider.get_users_create_update_service,
        IUsersPaginator: users_dependencies_provider.get_users_paginator,
        IUserFilterSet: users_dependencies_provider.get_users_filterset,
        UserPhotoService: users_dependencies_provider.get_user_photos_service,
    }


app = create_application(fastapi_dependency_overrides_factory, settings)
