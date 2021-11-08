from fastapi import Request
from sqlalchemy import select

from accounts.models import User


async def available_db_data(request: Request):
    request_user = request.state.user
    return select(User).where(User.id == request_user.id)
