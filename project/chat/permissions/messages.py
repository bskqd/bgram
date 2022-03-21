from typing import Optional

from fastapi import Request
from sqlalchemy import select

from accounts.models import User
from chat.models import chatroom_members_association_table, Message, MessagePhoto
from database.repository import BaseCRUDRepository
from mixins import permissions as mixins_permissions
from mixins.permissions import UserIsAuthenticatedPermission


class UserChatRoomMessagingPermissions(mixins_permissions.BasePermission):
    """
    Permissions service class for messaging in chat rooms for user.
    """

    def __init__(
            self,
            request_user: User,
            chat_room_id: int,
            db_repository: BaseCRUDRepository,
            request: Optional[Request] = None,
            message_id: Optional[int] = None
    ):
        self.request_user = request_user
        self.chat_room_id = chat_room_id
        self.db_repository = db_repository
        self.request = request
        self.message_id = message_id

    async def check_permissions(self):
        await UserIsAuthenticatedPermission(self.request_user).check_permissions()
        await self.check_user_is_member_of_chat_room()
        request_method = getattr(self.request, 'method', None)
        if request_method in {'PUT', 'PATCH', 'DELETE'}:
            await self.check_message_author()

    async def check_user_is_member_of_chat_room(self):
        self.db_repository.db_query = select(
            chatroom_members_association_table.c.room_id
        ).where(
            chatroom_members_association_table.c.user_id == self.request_user.id,
            chatroom_members_association_table.c.room_id == self.chat_room_id
        )
        if not await self.db_repository.exists():
            raise self.permission_denied_exception
        self.db_repository.db_query = None

    async def check_message_author(self):
        if not self.message_id:
            raise self.permission_denied_exception
        self.db_repository.db_query = select(
            Message
        ).where(
            Message.id == self.message_id,
            Message.author_id == self.request_user.id
        )
        if not await self.db_repository.exists():
            raise self.permission_denied_exception
        self.db_repository.db_query = None


class UserMessageFilesPermissions(mixins_permissions.BasePermission):
    def __init__(
            self,
            request_user: User,
            message_file_id: int,
            db_repository: BaseCRUDRepository,
    ):
        self.request_user = request_user
        self.message_file_id = message_file_id
        self.db_repository = db_repository

    async def check_permissions(self):
        await UserIsAuthenticatedPermission(self.request_user).check_permissions()
        await self.check_message_file_message_author()

    async def check_message_file_message_author(self):
        self.db_repository.db_query = select(
            MessagePhoto.id
        ).join(
            Message
        ).where(
            MessagePhoto.id == self.message_file_id,
            Message.author_id == self.request_user.id
        )
        request_user_is_message_author = await self.db_repository.exists()
        if not request_user_is_message_author:
            raise self.permission_denied_exception
        self.db_repository.db_query = None
