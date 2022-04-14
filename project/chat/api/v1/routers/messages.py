from typing import Optional, Tuple, Union

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, Form, Body
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy.sql import Select

from accounts.models import User
from chat.api.dependencies import chat as chat_dependencies
from chat.api.permissions.messages import UserChatRoomMessagingPermissions, UserMessageFilesPermissions
from chat.api.v1.filters.messages import MessagesFilterSet
from chat.api.v1.schemas.messages import ListMessagesSchema, UpdateMessageSchema, PaginatedListMessagesSchema
from chat.models import Message, MessagePhoto
from chat.services.messages import MessagesService, MessagesFilesServices
from chat.websockets.chat import WebSocketConnection, chat_rooms_websocket_manager
from database.repository import SQLAlchemyCRUDRepository
from mixins import views as mixins_views, dependencies as mixins_dependencies
from mixins.pagination import DefaultPaginationClass
from mixins.schemas import FilesSchema

router = APIRouter()


@router.websocket('/chat_rooms/{chat_room_id}/chat')
async def chat_websocket_endpoint(
        chat_room_id: int,
        websocket: WebSocket,
        request_user: User = Depends(chat_dependencies.get_request_user),
        db_session: AsyncSession = Depends(mixins_dependencies.db_session)
):
    db_repository = SQLAlchemyCRUDRepository(Message, db_session)
    permissions = UserChatRoomMessagingPermissions(request_user, chat_room_id, db_repository)
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
    pagination_class = DefaultPaginationClass
    filterset_class = MessagesFilterSet

    async def check_permissions(
            self,
            chat_room_id: int,
            db_repository: SQLAlchemyCRUDRepository,
            message_ids: Optional[Union[tuple[int], list[int]]] = None
    ):
        await UserChatRoomMessagingPermissions(
            request_user=self.request_user,
            chat_room_id=chat_room_id,
            db_repository=db_repository,
            request=self.request,
            message_ids=message_ids,
        ).check_permissions()

    def get_db_query(self, chat_room_id: int, *args) -> Select:
        return select(
            Message
        ).options(
            joinedload(Message.photos),
            contains_eager(Message.author)
        ).where(
            Message.chat_room_id == chat_room_id, *args
        ).order_by(-Message.id)

    @router.get('/chat_rooms/{chat_room_id}/messages', response_model=PaginatedListMessagesSchema)
    async def list_messages_view(self, chat_room_id: int):
        db_repository = SQLAlchemyCRUDRepository(Message, self.db_session)
        return await self.get_paginated_response(db_repository, self.filter_db_query(self.get_db_query(chat_room_id)))

    @router.post('/chat_rooms/{chat_room_id}/messages', response_model=ListMessagesSchema)
    async def create_message_view(
            self,
            chat_room_id: int,
            text: str = Form(...),
            files: Optional[Tuple[UploadFile]] = None
    ):
        db_repository = SQLAlchemyCRUDRepository(Message, self.db_session)
        await self.check_permissions(chat_room_id, db_repository)
        return await MessagesService(db_repository, chat_room_id).create_message(
            text, files=files, author_id=self.request_user.id,
        )

    @router.patch('/chat_rooms/{chat_room_id}/messages/{message_id}', response_model=ListMessagesSchema)
    async def update_message_view(
            self,
            chat_room_id: int,
            message_id: int,
            message_data: UpdateMessageSchema
    ):
        db_repository = SQLAlchemyCRUDRepository(Message, self.db_session)
        await self.check_permissions(chat_room_id, db_repository, message_ids=(message_id,))
        db_repository.db_query = self.get_db_query(chat_room_id)
        message = await db_repository.get_one(Message.id == message_id)
        return await MessagesService(db_repository, chat_room_id).update_message(
            message, **message_data.dict(exclude_unset=True)
        )

    @router.delete('/chat_rooms/{chat_room_id}/messages')
    async def delete_messages_view(self, chat_room_id: int, message_ids: list[int] = Body(...)):
        db_repository = SQLAlchemyCRUDRepository(Message, self.db_session)
        await self.check_permissions(chat_room_id, db_repository, message_ids=message_ids)
        await MessagesService(db_repository, chat_room_id).delete_messages(message_ids)
        return {'detail': 'success'}


@router.patch('/message/{message_id}/message_files/{message_file_id}', response_model=FilesSchema)
async def replace_message_photo(
        message_id: int,
        message_file_id: int,
        file: UploadFile,
        db_session: AsyncSession = Depends(mixins_dependencies.db_session),
        request_user: Optional[User] = Depends(mixins_dependencies.get_request_user)
) -> dict:
    db_repository = SQLAlchemyCRUDRepository(MessagePhoto, db_session)
    await UserMessageFilesPermissions(request_user, message_file_id, db_repository).check_permissions()
    return await MessagesFilesServices(message_id, message_file_id, db_repository).change_message_file(file)


@router.delete('/message/{message_id}/message_files/{message_file_id}')
async def delete_message_photo(
        message_id: int,
        message_file_id: int,
        db_session: AsyncSession = Depends(mixins_dependencies.db_session),
        request_user: Optional[User] = Depends(mixins_dependencies.get_request_user)
) -> dict:
    db_repository = SQLAlchemyCRUDRepository(MessagePhoto, db_session)
    await UserMessageFilesPermissions(request_user, message_file_id, db_repository).check_permissions()
    await MessagesFilesServices(message_id, message_file_id, db_repository).delete_message_file()
    return {'status': 'success'}
