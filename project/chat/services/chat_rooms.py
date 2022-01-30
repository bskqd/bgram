from typing import Optional, List, Any, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import Select

from accounts.models import User
from chat.models import ChatRoom
from mixins.services.crud import CRUDOperationsService


class ChatRoomService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_chat_room(self, name: str, members_ids: List[int], **kwargs) -> ChatRoom:
        chat_room = ChatRoom(name=name, **kwargs)
        crud_operations_service = CRUDOperationsService(self.db_session)
        chat_room = await crud_operations_service.create_object_in_database(chat_room)
        chat_room = await crud_operations_service.get_object(
            select(ChatRoom).options(joinedload(ChatRoom.members).load_only(User.id)), ChatRoom, chat_room.id,
        )
        members = await self.db_session.scalars(select(User).where(User.id.in_(members_ids)))
        chat_room.members.extend(members.all())
        return chat_room

    async def retrieve_chat_room(
            self,
            search_value: Any,
            lookup_kwarg: str = 'id',
            queryset: Select = select(ChatRoom)
    ) -> ChatRoom:
        return await CRUDOperationsService(self.db_session).get_object(
            queryset, ChatRoom, search_value, lookup_kwarg=lookup_kwarg
        )

    async def list_chat_rooms(self, queryset: Optional[Select] = select(ChatRoom)) -> List[ChatRoom]:
        chat_rooms = await self.db_session.scalars(queryset)
        return chat_rooms.unique().all()

    async def update_chat_room(
            self,
            chat_room: ChatRoom,
            members: Optional[Iterable[User]] = None,
            **data_for_update
    ) -> ChatRoom:
        if members is not None:
            data_for_update['members'] = members
        return await CRUDOperationsService(self.db_session).update_object_in_database(chat_room, **data_for_update)
