from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from accounts.models import User
from chat.models import ChatRoom


async def available_db_data(request: Request):
    return select(
        User
    ).where(
        User.id == request.state.user.id
    ).options(
        joinedload(User.chat_rooms).load_only(ChatRoom.id),
        joinedload(User.photos)
    )
