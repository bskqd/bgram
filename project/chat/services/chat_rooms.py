from typing import Optional, List, Any, Union, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import Select

from accounts.models import User
from chat.models import ChatRoom
from mixins.services.crud import CRUDOperationsService


async def create_chat_room(name: str, members_ids: List[int], db_session: Session, **kwargs) -> ChatRoom:
    chat_room = ChatRoom(name=name, **kwargs)
    crud_operations_service = CRUDOperationsService(db_session)
    chat_room = await crud_operations_service.create_object_in_database(chat_room)
    chat_room = await crud_operations_service.get_object(
        select(ChatRoom).options(joinedload(ChatRoom.members).load_only(User.id)), ChatRoom, chat_room.id,
    )
    members = await db_session.execute(select(User).where(User.id.in_(members_ids)))
    chat_room.members.extend(members.scalars().all())
    return chat_room


async def get_chat_rooms(
        db_session: Session,
        queryset: Optional[Select] = select(ChatRoom),
) -> List[ChatRoom]:
    chat_rooms = await db_session.execute(queryset)
    return chat_rooms.unique().scalars().all()


async def get_chat_room(
        search_value: Any,
        db_session: Session,
        lookup_kwarg: str = 'id',
        queryset: Select = select(ChatRoom)
) -> ChatRoom:
    return await CRUDOperationsService(db_session).get_object(
        queryset, ChatRoom, search_value, lookup_kwarg=lookup_kwarg
    )


async def update_chat_room(
        chat_room: ChatRoom,
        db_session: Session,
        members: Optional[Union[List[User], Tuple[User]]] = None,
        **data_for_update
) -> ChatRoom:
    if members is not None:
        data_for_update['members'] = members
    return await CRUDOperationsService(db_session).update_object_in_database(
        chat_room, **data_for_update
    )

#
# async def create_user_photo(
#         user_id: int,
#         file: UploadFile,
#         db_session: Optional[Session] = Depends(mixins_dependencies.db_session),
# ) -> UserPhoto:
#     return await mixins_utils.create_object_file(UserPhoto, file, db_session=db_session, user_id=user_id)
