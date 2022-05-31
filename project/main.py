from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.staticfiles import StaticFiles

import core.dependencies as dependencies
from accounts.models import User
from core.config import settings
from core.middleware.authentication import JWTAuthenticationMiddleware
from core.routers import v1

app = FastAPI()

app.add_middleware(JWTAuthenticationMiddleware)

app.mount(f'/{settings.MEDIA_URL}', StaticFiles(directory=settings.MEDIA_PATH), name='media')

app.include_router(v1.router, prefix='/api/v1')

app.dependency_overrides[AsyncSession] = dependencies.db_session
app.dependency_overrides[User] = dependencies.get_request_user
app.dependency_overrides[dependencies.EventPublisher] = dependencies.get_event_publisher
app.dependency_overrides[dependencies.EventReceiver] = dependencies.get_event_receiver
