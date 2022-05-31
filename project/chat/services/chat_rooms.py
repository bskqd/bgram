from typing import Optional, List, Iterable, Union

from sqlalchemy import select
from sqlalchemy.sql import Select

from accounts.models import User
from chat.models import ChatRoom, chatroom_members_association_table
from core.database.repository import BaseCRUDRepository


class ChatRoomService:
    def __init__(self, db_repository: BaseCRUDRepository):
        self.db_repository = db_repository

    async def retrieve_chat_room(self, *args, db_query: Optional[Select] = None) -> User:
        if db_query is not None:
            self.db_repository.db_query = db_query
        return await self.db_repository.get_one(*args)

    async def create_chat_room(self, name: str, members_ids: List[int], **kwargs) -> ChatRoom:
        self.db_repository.db_query = select(User).where(User.id.in_(members_ids))
        members = await self.db_repository.get_many()
        chat_room = ChatRoom(name=name, members=members, **kwargs)
        chat_room = await self.db_repository.create(chat_room)
        await self.db_repository.commit()
        await self.db_repository.refresh(chat_room)
        return chat_room

    async def update_chat_room(
            self,
            chat_room: ChatRoom,
            members: Optional[Iterable[User]] = None,
            **data_for_update
    ) -> ChatRoom:
        if members is not None:
            data_for_update['members'] = members
        chat_room = await self.db_repository.update_object(chat_room, **data_for_update)
        await self.db_repository.commit()
        await self.db_repository.refresh(chat_room)
        return chat_room

    async def get_user_chat_room_ids(self, user: Union[int, User]) -> list:
        user_id = user if isinstance(user, int) else user.id
        self.db_repository.db_query = select(
            chatroom_members_association_table.c.room_id
        ).where(
            chatroom_members_association_table.c.user_id == user_id
        )
        chat_room_ids = await self.db_repository.get_many()
        self.db_repository.db_query = None
        return chat_room_ids
