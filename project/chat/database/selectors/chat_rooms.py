from accounts.models import User
from chat.models import ChatRoom, chatroom_members_association_table
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select


def get_chat_rooms_db_query(request_user: User) -> Select:
    return (
        select(
            ChatRoom,
        )
        .join(
            chatroom_members_association_table,
        )
        .options(
            joinedload(ChatRoom.members).load_only(User.id),
            joinedload(ChatRoom.photos),
        )
        .where(
            chatroom_members_association_table.c.user_id == request_user.id,
        )
    )
