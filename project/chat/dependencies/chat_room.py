from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from accounts.models import User
from chat.models import ChatRoom


async def available_db_data(request: Request):
    return select(ChatRoom).join(
        User.chat_rooms
    ).options(
        joinedload(ChatRoom.members)
    ).where(
        User.id == request.state.user.id
    )
