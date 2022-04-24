from typing import Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.models import User
from database.base import DatabaseSession
from main import app


async def db_session() -> DatabaseSession:
    async with (session := DatabaseSession()):
        yield session


async def get_request(request: Request) -> Request:
    return request


async def get_request_user(request: Request) -> Optional[User]:
    return request.state.user

app.dependency_overrides[AsyncSession] = db_session
app.dependency_overrides[User] = get_request_user
app.dependency_overrides[Request] = get_request
