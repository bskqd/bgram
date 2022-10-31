from typing import Callable

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from accounts.dependencies.authorization.dependencies import AuthorizationDependenciesOverrides
from accounts.dependencies.users.dependencies import UsersDependenciesOverrides
from chat.dependencies.chat_rooms.dependencies import ChatRoomsDependenciesOverrides
from chat.dependencies.messages.dependencies import MessagesDependenciesOverrides
from core.authentication.middlewares import JWTAuthenticationMiddleware
from core.config import SettingsABC
from core.contrib.redis import redis_client
from core.database.base import provide_db_sessionmaker
from core.dependencies.dependencies import FastapiDependenciesOverrides
from core.dependencies.providers import provide_settings
from core.routers import v1
from core.tasks_scheduling.arq_settings import create_arq_redis_pool
from core.tasks_scheduling.dependencies import TaskSchedulerDependenciesOverrides


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
        **dependencies_overrides.override_dependencies(),
        **tasks_scheduler_dependencies_overrides.override_dependencies(),
        **users_dependencies_overrides.override_dependencies(),
        **authorization_dependencies_overrides.override_dependencies(),
        **messages_dependencies_overrides.override_dependencies(),
        **chat_rooms_dependencies_overrides.override_dependencies(),
    }


app = create_application(fastapi_dependency_overrides_factory, provide_settings())


@app.on_event('startup')
async def open_connections():
    app.state.arq_redis_pool = await create_arq_redis_pool()


@app.on_event('shutdown')
async def close_connections():
    provide_db_sessionmaker().close_all()
    await redis_client.close()
    await app.state.arq_redis_pool.close()
