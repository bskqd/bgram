from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select

from accounts.models import User
from chat.models import ChatRoom


async def get_available_chat_rooms_for_user(request: Request) -> Select:
    return select(
        ChatRoom, ChatRoom.members_count
    ).options(
        joinedload(ChatRoom.members).load_only(User.id), joinedload(ChatRoom.photos)
    ).where(
        User.id == request.state.user.id
    )
