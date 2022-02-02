from typing import Optional

from fastapi import Request

from accounts.models import User
from database import DatabaseSession


async def db_session() -> DatabaseSession:
    async with (session := DatabaseSession()):
        yield session


async def get_request(request: Request) -> Request:
    return request


async def get_request_user(request: Request) -> Optional[User]:
    return request.state.user
