
from typing import Optional, List, Any

from sqlalchemy import select
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.orm import Session, joinedload

from accounts.models import User
from chat.models import ChatRoom
from mixins import utils as mixins_utils


async def create_chat_room(name: str, members_ids: List[int], db_session: Session, **kwargs) -> ChatRoom:
    chat_room = ChatRoom(name=name, **kwargs)
    chat_room = await mixins_utils.create_object_in_database(chat_room, db_session)
    chat_room = await mixins_utils.get_object(
        select(ChatRoom).options(joinedload(ChatRoom.members).load_only(User.id)), ChatRoom, chat_room.id, db_session
    )
    members = await db_session.execute(select(User).where(User.id.in_(members_ids)))
    chat_room.members.extend(members.scalars().all())
    return chat_room


async def get_chat_rooms(
        db_session: Session,
        available_db_data: Optional[ChunkedIteratorResult] = select(ChatRoom),
) -> List[ChatRoom]:
    chat_rooms = await db_session.execute(available_db_data)
    return chat_rooms.unique().scalars().all()


async def get_chat_room(
        search_value: Any,
        db_session: Session,
        lookup_kwarg: str = 'id',
        available_db_data: ChunkedIteratorResult = select(ChatRoom)
) -> ChatRoom:
    return await mixins_utils.get_object(
        available_db_data, ChatRoom, search_value, db_session=db_session, lookup_kwarg=lookup_kwarg
    )


async def update_chat_room(
        chat_room: ChatRoom,
        db_session: Session,
        **data_for_update
) -> ChatRoom:
    return await mixins_utils.update_object_in_database(chat_room, db_session, **data_for_update)

#
# async def create_user_photo(
#         user_id: int,
#         file: UploadFile,
#         db_session: Optional[Session] = Depends(mixins_dependencies.db_session),
# ) -> UserPhoto:
#     return await mixins_utils.create_object_file(UserPhoto, file, db_session=db_session, user_id=user_id)
