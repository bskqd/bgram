import functools

from accounts.models import User
from chat.models import ChatRoom, chatroom_members_association_table
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql import Select


def get_many_chat_rooms_db_query_by_user(user_id: int, *args) -> Select:
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
            chatroom_members_association_table.c.user_id == user_id,
            *args,
        )
    )


# TODO: find out not a hacky way of counting members_count
# def get_one_chat_room_db_query_by_user(user_id: int, *args) -> Select:
#     members_count_subquery = select(
#         ChatRoom.id,
#         func.count(chatroom_members_association_table.c.member_type).label('members_count')
#     ).join(
#         chatroom_members_association_table
#     ).group_by(
#         ChatRoom.id,
#     ).subquery()
#     return (
#             select(
#                 ChatRoom,
#                 # members_count_subquery.c.members_count,
#                 # ChatRoom.members_count,
#             )
#             .join(
#                 chatroom_members_association_table, chatroom_members_association_table.c.room_id == ChatRoom.id,
#             )
#             # .join(
#             #     members_count_subquery, members_count_subquery.c.id == ChatRoom.id, isouter=True,
#             # )
#             .options(
#                 joinedload(ChatRoom.photos),
#             )
#             .where(
#                 chatroom_members_association_table.c.user_id == user_id,
#                 *args,
#             )
#         )


@functools.lru_cache(maxsize=1)
def get_chat_room_creation_relations_to_load() -> tuple:
    return selectinload(ChatRoom.members).load_only(User.id), joinedload(ChatRoom.photos)
