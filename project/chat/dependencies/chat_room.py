from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from accounts.models import User
from chat.models import ChatRoom


async def available_db_data(request: Request):
    request_user = request.state.user
    return select(ChatRoom).where(ChatRoom.id == request_user.id)
