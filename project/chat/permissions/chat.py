from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from accounts.models import User
from chat.constants.messages import MessagesActionTypeEnum
from chat.models import chatroom_members_association_table, Message
from mixins import permissions as mixins_permissions


class UserChatRoomMessagingPermissions(mixins_permissions.PermissionsRepository):
    """
    Permissions service class for messaging in chat rooms for user.
    """

    def __init__(self, request_user: User, chat_room_id: int, db_session: Session):
        self.request_user = request_user
        self.chat_room_id = chat_room_id
        self.db_session = db_session

    async def check_permissions(self) -> bool:
        return await self.check_user_is_member_of_chat_room()

    async def check_user_is_member_of_chat_room(self) -> bool:
        request_user_is_member_of_chat_room_query = select(
            chatroom_members_association_table.c.room_id
        ).where(
            chatroom_members_association_table.c.user_id == self.request_user.id,
            chatroom_members_association_table.c.room_id == self.chat_room_id
        ).exists().select()
        request_user_is_member_of_chat_room = await self.db_session.execute(request_user_is_member_of_chat_room_query)
        return request_user_is_member_of_chat_room.scalar()

    async def check_message_action(self, action: str, message_id: Optional[int] = None) -> bool:
        if action == MessagesActionTypeEnum.CREATE.value:
            return True
        if action in {MessagesActionTypeEnum.UPDATE.value, MessagesActionTypeEnum.DELETE.value}:
            message = await self.db_session.execute(
                select(Message).options(joinedload(Message.author).load_only(User.id)).where(Message.id == message_id)
            )
            message = message.scalar()
            return getattr(message, 'author_id', None) == self.request_user.id
