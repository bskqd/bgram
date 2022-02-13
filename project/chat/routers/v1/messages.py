from typing import Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

import chat.dependencies.messages
from accounts.models import User
from chat.models import Message
from chat.permissions.messages import UserChatRoomMessagingPermissions
from chat.schemas.messages import (ListMessagesSchema, CreateMessageSchema, UpdateMessageSchema,
                                   PaginatedListMessagesSchema)
from chat.services.messages import WebSocketConnection, MessagesService
from chat.services.messages import chat_rooms_websocket_manager
from database.repository import SQLAlchemyCRUDRepository
from mixins import views as mixins_views, dependencies as mixins_dependencies
from mixins.pagination import DefaultPaginationClass
from mixins.permissions import UserIsAuthenticatedPermission

router = APIRouter()


@router.websocket('/chat_rooms/{chat_room_id}/chat')
async def chat_websocket_endpoint(
        chat_room_id: int,
        websocket: WebSocket,
        request_user: User = Depends(chat.dependencies.messages.get_request_user),
        db_session: AsyncSession = Depends(mixins_dependencies.db_session)
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
    db_session: AsyncSession = Depends(mixins_dependencies.db_session)
    pagination_class = DefaultPaginationClass

    async def check_permissions(self, chat_room_id: int, message_id: Optional[int] = None):
        await UserIsAuthenticatedPermission(self.request_user).check_permissions()
        await UserChatRoomMessagingPermissions(
            request_user=self.request_user,
            chat_room_id=chat_room_id,
            db_session=self.db_session,
            request=self.request,
            message_id=message_id,
        ).check_permissions()

    def get_db_query(self, chat_room_id: int, *args) -> Select:
        return select(Message).where(Message.chat_room_id == chat_room_id, *args).order_by(-Message.id)

    @router.get('/chat_rooms/{chat_room_id}/messages', response_model=PaginatedListMessagesSchema)
    async def list_messages_view(self, chat_room_id: int):
        await self.check_permissions(chat_room_id)
        db_repository = SQLAlchemyCRUDRepository(Message, self.db_session)
        return self.get_paginated_response(
            await MessagesService(db_repository, chat_room_id).list_messages(self.get_db_query(chat_room_id))
        )

    @router.post('/chat_rooms/{chat_room_id}/messages', response_model=ListMessagesSchema)
    async def create_message_view(self, chat_room_id: int, message_data: CreateMessageSchema):
        await self.check_permissions(chat_room_id)
        db_repository = SQLAlchemyCRUDRepository(Message, self.db_session)
        return await MessagesService(db_repository, chat_room_id).create_message(
            message_data.text, self.request_user.id,
        )

    @router.patch('/chat_rooms/{chat_room_id}/messages/{message_id}', response_model=ListMessagesSchema)
    async def update_message_view(
            self,
            chat_room_id: int,
            message_id: int,
            message_data: UpdateMessageSchema
    ):
        await self.check_permissions(chat_room_id, message_id=message_id)
        db_repository = SQLAlchemyCRUDRepository(Message, self.db_session, db_query=self.get_db_query(chat_room_id))
        message = await db_repository.get_one(Message.id == message_id)
        return await MessagesService(db_repository, chat_room_id).update_message(
            message, **message_data.dict(exclude_unset=True)
        )

    @router.delete('/chat_rooms/{chat_room_id}/messages/{message_id}')
    async def delete_message_view(self, chat_room_id: int, message_id: int):
        await self.check_permissions(chat_room_id, message_id=message_id)
        db_repository = SQLAlchemyCRUDRepository(Message, self.db_session)
        await MessagesService(db_repository, chat_room_id).delete_message(message_id)
        return {'detail': 'success'}
