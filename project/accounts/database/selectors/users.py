import functools

from accounts.models import User
from chat.models import ChatRoom, chatroom_members_association_table
from sqlalchemy import or_, select, true
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql import Select


def get_users_db_query(request_user: User) -> Select:
    return (
        select(
            User,
        )
        .join(
            chatroom_members_association_table,
            isouter=True,
        )
        .options(
            selectinload(User.chat_rooms).load_only(ChatRoom.id),
            joinedload(User.photos),
        )
        .where(
            or_(User.id == request_user.id, chatroom_members_association_table.c.user_id == request_user.id),
            User.is_active == true(),
        )
    )


@functools.lru_cache(maxsize=1)
def get_user_update_returning_options() -> tuple:
    return selectinload(User.chat_rooms).load_only(ChatRoom.id), joinedload(User.photos)
