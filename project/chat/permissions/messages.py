from typing import Optional

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from accounts.models import User
from chat.models import chatroom_members_association_table, Message
from mixins import permissions as mixins_permissions


class UserChatRoomMessagingPermissions(mixins_permissions.BasePermission):
    """
    Permissions service class for messaging in chat rooms for user.
    """

    def __init__(
            self,
            request_user: User,
            chat_room_id: int,
            db_session: Session,
            request: Optional[Request] = None,
            message_id: Optional[int] = None
    ):
        self.request_user = request_user
        self.chat_room_id = chat_room_id
        self.db_session = db_session
        self.request = request
        self.message_id = message_id

    async def check_permissions(self):
        await self.check_user_is_member_of_chat_room()
        request_method = getattr(self.request, 'method', None)
        if request_method in {'PUT', 'PATCH', 'DELETE'}:
            await self.check_message_author()

    async def check_user_is_member_of_chat_room(self):
        request_user_is_member_of_chat_room_query = select(
            chatroom_members_association_table.c.room_id
        ).where(
            chatroom_members_association_table.c.user_id == self.request_user.id,
            chatroom_members_association_table.c.room_id == self.chat_room_id
        ).exists().select()
        request_user_is_member_of_chat_room = await self.db_session.scalar(request_user_is_member_of_chat_room_query)
        if not request_user_is_member_of_chat_room:
            raise self.permission_denied_exception

    async def check_message_author(self):
        if not self.message_id:
            raise self.permission_denied_exception
        request_user_is_message_author = await self.db_session.scalar(
            select(Message).options(
                joinedload(Message.author).load_only(User.id)
            ).where(
                Message.id == self.message_id
            ).exists().select()
        )
        if not request_user_is_message_author:
            raise self.permission_denied_exception
