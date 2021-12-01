from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from accounts.models import User
from chat.models import ChatRoom


async def available_db_data(request: Request):
    return select(
        ChatRoom, ChatRoom.members_count
    ).options(
        joinedload(ChatRoom.members).load_only(User.id), joinedload(ChatRoom.photos)
    ).where(
        User.id == request.state.user.id
    )
