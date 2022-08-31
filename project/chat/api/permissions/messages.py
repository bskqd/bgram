from typing import Optional, Union

from fastapi import Request
from sqlalchemy import select

from accounts.models import User
from chat.models import chatroom_members_association_table, Message, MessagePhoto
from core import permissions as mixins_permissions
from core.database.repository import BaseDatabaseRepository
from core.permissions import UserIsAuthenticatedPermission


class UserChatRoomMessagingPermissions(mixins_permissions.BasePermission):
    """
    Permissions service class for messaging in chat rooms for user.
    """

    def __init__(
            self,
            request_user: User,
            chat_room_id: int,
            db_repository: BaseDatabaseRepository,
            request: Optional[Request] = None,
            message_ids: Optional[Union[tuple[int], list[int]]] = None
    ):
        self.request_user = request_user
        self.chat_room_id = chat_room_id
        self.db_repository = db_repository
        self.request = request
        self.message_ids = message_ids

    async def check_permissions(self):
        await UserIsAuthenticatedPermission(self.request_user).check_permissions()
        await self.check_user_is_member_of_chat_room()
        request_method = getattr(self.request, 'method', None)
        if request_method in {'PUT', 'PATCH', 'DELETE'}:
            await self.check_message_author()

    async def check_user_is_member_of_chat_room(self):
        is_user_member_of_chat_room_query = select(
            chatroom_members_association_table.c.room_id
        ).where(
            chatroom_members_association_table.c.user_id == self.request_user.id,
            chatroom_members_association_table.c.room_id == self.chat_room_id
        )
        if not await self.db_repository.exists(db_query=is_user_member_of_chat_room_query):
            raise self.permission_denied_exception

    async def check_message_author(self):
        if not self.message_ids:
            raise self.permission_denied_exception
        is_user_message_author_query = select(
            Message
        ).where(
            Message.id.in_(self.message_ids),
            Message.author_id == self.request_user.id
        )
        if not await self.db_repository.exists(db_query=is_user_message_author_query):
            raise self.permission_denied_exception


class UserMessageFilesPermissions(mixins_permissions.BasePermission):
    def __init__(
            self,
            request_user: User,
            message_file_id: int,
            db_repository: BaseDatabaseRepository,
    ):
        self.request_user = request_user
        self.message_file_id = message_file_id
        self.db_repository = db_repository

    async def check_permissions(self):
        await UserIsAuthenticatedPermission(self.request_user).check_permissions()
        await self.check_message_file_message_author()

    async def check_message_file_message_author(self):
        is_request_user_message_author_query = select(
            MessagePhoto.id
        ).join(
            Message
        ).where(
            MessagePhoto.id == self.message_file_id,
            Message.author_id == self.request_user.id
        )
        if not await self.db_repository.exists(db_query=is_request_user_message_author_query):
            raise self.permission_denied_exception
