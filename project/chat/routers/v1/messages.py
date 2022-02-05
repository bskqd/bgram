from typing import Optional

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi_utils.cbv import cbv
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

import chat.dependencies.messages
from accounts.models import User
from chat.dependencies import messages as messages_dependencies
from chat.permissions.messages import UserChatRoomMessagingPermissions
from chat.schemas.messages import (ListMessagesSchema, CreateMessageSchema, UpdateMessageSchema,
                                   PaginatedListMessagesSchema)
from chat.services.messages import WebSocketConnection, MessagesService
from chat.services.messages import chat_rooms_websocket_manager
from mixins import views as mixins_views, dependencies as mixins_dependencies
from mixins.pagination import DefaultPaginationClass
from mixins.permissions import UserIsAuthenticatedPermission

router = APIRouter()


@router.websocket('/chat_rooms/{chat_room_id}/chat')
async def chat_websocket_endpoint(
        chat_room_id: int,
        websocket: WebSocket,
        request_user: User = Depends(chat.dependencies.messages.get_request_user),
        db_session: Session = Depends(mixins_dependencies.db_session)
):
    permissions = UserChatRoomMessagingPermissions(request_user, chat_room_id, db_session)
    try:
        await permissions.check_permissions()
    except HTTPException:
        return await websocket.close()
    websocket_connection = WebSocketConnection(websocket, request_user, chat_room_id)
    await chat_rooms_websocket_manager.connect(websocket_connection)
    try:
        await websocket.receive()
        raise WebSocketDisconnect
    except WebSocketDisconnect:
        await chat_rooms_websocket_manager.disconnect(websocket_connection)
        await chat_rooms_websocket_manager.broadcast({'Client': 'has left the chat'}, chat_room_id)


@cbv(router)
class MessagesView(mixins_views.AbstractView):
    queryset: Select = Depends(messages_dependencies.get_messages_queryset)
    db_session: Session = Depends(mixins_dependencies.db_session)
    request_user: Optional[User] = Depends(mixins_dependencies.get_request_user)
    paginator_class = DefaultPaginationClass

    async def check_permissions(self, chat_room_id: int, request: Request, message_id: Optional[int] = None):
        await UserIsAuthenticatedPermission(self.request_user).check_permissions()
        await UserChatRoomMessagingPermissions(
            request_user=self.request_user,
            chat_room_id=chat_room_id,
            db_session=self.db_session,
            request=request,
            message_id=message_id,
        ).check_permissions()

    @router.get('/chat_rooms/{chat_room_id}/messages', response_model=PaginatedListMessagesSchema)
    async def list_messages_view(self, chat_room_id: int):
        await self.check_permissions(chat_room_id, self.request)
        return self.paginator_class(self.request).paginate(
            await MessagesService(self.db_session).list_messages(chat_room_id, self.queryset)
        )

    @router.post('/chat_rooms/{chat_room_id}/messages', response_model=ListMessagesSchema)
    async def create_message_view(self, chat_room_id: int, message_data: CreateMessageSchema):
        request_user_id = self.request_user.id
        await self.check_permissions(chat_room_id, self.request)
        return await MessagesService(db_session=self.db_session).create_message(
            chat_room_id, message_data.text, request_user_id,
        )

    @router.patch('/chat_rooms/{chat_room_id}/messages/{message_id}', response_model=ListMessagesSchema)
    async def update_message_view(
            self,
            chat_room_id: int,
            message_id: int,
            message_data: UpdateMessageSchema
    ):
        await self.check_permissions(chat_room_id, self.request, message_id=message_id)
        return await MessagesService(db_session=self.db_session, chat_room_id=chat_room_id).update_message(
            message_id, **message_data.dict(exclude_unset=True)
        )

    @router.delete('/chat_rooms/{chat_room_id}/messages/{message_id}')
    async def delete_message_view(self, chat_room_id: int, message_id: int):
        await self.check_permissions(chat_room_id, self.request, message_id=message_id)
        await MessagesService(db_session=self.db_session, chat_room_id=chat_room_id).delete_message(message_id)
        return {'detail': 'success'}
