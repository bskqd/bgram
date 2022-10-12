from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select

from accounts.models import User
from chat.models import chatroom_members_association_table, ChatRoom


def get_users_db_query(request_user: User) -> Select:
    return select(
        User,
    ).join(
        chatroom_members_association_table,
    ).options(
        joinedload(User.chat_rooms).load_only(ChatRoom.id), joinedload(User.photos),
    ).where(
        chatroom_members_association_table.c.user_id == request_user.id,
    )
