from typing import List, Optional

from fastapi import APIRouter, Depends, Request
from fastapi_utils.cbv import cbv
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from accounts.models import User
from chat.constants.messages import MessagesActionTypeEnum
from chat.dependencies import messages as messages_dependencies
from chat.permissions.chat import UserChatRoomMessagingPermissions
from chat.schemas.messages import ListMessagesSchema, CreateMessageSchema, UpdateMessageSchema
from chat.services.chat import chat_rooms_websocket_manager
from chat.services.messages import MessagesService
from mixins import views as mixins_views, dependencies as mixins_dependencies

router = APIRouter()


@cbv(router)
class MessagesView(mixins_views.AbstractView):
    queryset: Select = Depends(messages_dependencies.get_messages_queryset)
    db_session: Session = Depends(mixins_dependencies.db_session)
    request_user: Optional[User] = Depends(mixins_dependencies.get_request_user)

    async def check_permissions(self, chat_room_id: int, request: Request, message_id: Optional[int] = None):
        await UserChatRoomMessagingPermissions(
            request_user=self.request_user,
            chat_room_id=chat_room_id,
            db_session=self.db_session,
            request=request,
            message_id=message_id,
        ).check_permissions()

    @router.post('/chat_rooms/{chat_room_id}/messages', response_model=ListMessagesSchema)
    async def create_message_view(self, request: Request, chat_room_id: int, message_data: CreateMessageSchema):
        request_user_id = self.request_user.id
        await self.check_permissions(chat_room_id, request)
        created_message = await MessagesService(db_session=self.db_session).create_message(
            chat_room_id, message_data.text, request_user_id,
        )
        await self._broadcast_message_to_chat_room(
            chat_room_id, MessagesActionTypeEnum.CREATED.value, ListMessagesSchema.from_orm(created_message).dict(),
        )
        return created_message

    @router.patch('/chat_rooms/{chat_room_id}/messages/{message_id}', response_model=ListMessagesSchema)
    async def update_message_view(
            self,
            request: Request,
            chat_room_id: int,
            message_id: int,
            message_data: UpdateMessageSchema
    ):
        await self.check_permissions(chat_room_id, request, message_id=message_id)
        updated_message = await MessagesService(db_session=self.db_session).update_message(
            message_id, **message_data.dict(exclude_unset=True)
        )
        await self._broadcast_message_to_chat_room(
            chat_room_id, MessagesActionTypeEnum.UPDATED.value, ListMessagesSchema.from_orm(updated_message).dict(),
        )
        return updated_message

    @router.delete('/chat_rooms/{chat_room_id}/messages/{message_id}')
    async def update_message_view(self, request: Request, chat_room_id: int, message_id: int):
        await self.check_permissions(chat_room_id, request, message_id=message_id)
        await MessagesService(db_session=self.db_session).delete_message(message_id)
        await self._broadcast_message_to_chat_room(
            chat_room_id, MessagesActionTypeEnum.DELETED.value, {'message_id': message_id},
        )
        return {'detail': 'success'}

    @staticmethod
    async def _broadcast_message_to_chat_room(chat_room_id: int, action: str, message_data: dict):
        await chat_rooms_websocket_manager.broadcast(
            message={'action': action, **message_data},
            chat_room_id=chat_room_id
        )

    @router.get('/chat_rooms/{chat_room_id}/messages', response_model=List[ListMessagesSchema])
    async def list_messages_view(self, request: Request, chat_room_id: int):
        await self.check_permissions(chat_room_id, request)
        return await MessagesService(self.db_session).list_messages(chat_room_id, self.queryset)
