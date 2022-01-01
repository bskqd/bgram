from sqlalchemy import select
from sqlalchemy.orm import Session

from accounts.models import User
from chat.models import chatroom_members_association_table
from mixins import permissions as mixins_permissions


class UserChatRoomMessagingPermissionsService(mixins_permissions.PermissionsServiceABC):
    """
    Permissions service class for messaging in chat rooms for user.
    """

    def __init__(self, request_user: User, chat_room_id: int, db_session: Session):
        self.request_user = request_user
        self.chat_room_id = chat_room_id
        self.db_session = db_session

    async def check_permissions(self) -> bool:
        return await self.check_user_is_member_of_chat_room

    @property
    async def check_user_is_member_of_chat_room(self) -> bool:
        request_user_is_member_of_chat_room_query = select(
            chatroom_members_association_table.c.room_id
        ).where(
            chatroom_members_association_table.c.user_id == self.request_user.id,
            chatroom_members_association_table.c.room_id == self.chat_room_id
        ).exists().select()
        request_user_is_member_of_chat_room = await self.db_session.execute(request_user_is_member_of_chat_room_query)
        return request_user_is_member_of_chat_room.scalar()
