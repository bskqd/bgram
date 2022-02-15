from typing import Optional, List, Iterable

from sqlalchemy import select

from accounts.models import User
from chat.models import ChatRoom
from database.repository import SQLAlchemyCRUDRepository


class ChatRoomService:
    def __init__(self, db_repository: SQLAlchemyCRUDRepository):
        self.db_repository = db_repository

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
