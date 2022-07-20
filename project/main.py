from typing import Callable

from fastapi import FastAPI
from pydantic import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.staticfiles import StaticFiles

from accounts.models import User
from core.config import settings
from core.dependencies import EventPublisher, EventReceiver, FastapiDependenciesProvider
from core.middleware.authentication import JWTAuthenticationMiddleware
from core.routers import v1


def create_application(dependency_overrides_factory: Callable, config: BaseSettings) -> FastAPI:
    application = FastAPI()

    application.add_middleware(JWTAuthenticationMiddleware)

    application.mount(f'/{config.MEDIA_URL}', StaticFiles(directory=config.MEDIA_PATH), name='media')

    application.include_router(v1.router, prefix='/api/v1')

    dependencies_provider = FastapiDependenciesProvider(config)
    application.dependency_overrides = dependency_overrides_factory(dependencies_provider)

    return application


def fastapi_dependency_overrides_factory(dependencies_provider: FastapiDependenciesProvider) -> dict:
    return {
        AsyncSession: dependencies_provider.get_db_session,
        User: dependencies_provider.get_request_user,
        EventPublisher: dependencies_provider.get_event_publisher,
        EventReceiver: dependencies_provider.get_event_receiver,
    }


app = create_application(fastapi_dependency_overrides_factory, settings)
