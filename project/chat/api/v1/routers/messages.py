from typing import Optional, Tuple

from fastapi import (
    APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, Form, Request, Query,
)
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.models import User
from chat.api.dependencies import chat as chat_dependencies
from chat.api.dependencies.chat_rooms import get_chat_rooms_retrieve_service
from chat.api.dependencies.messages import get_messages_filterset
from chat.api.permissions.messages import UserChatRoomMessagingPermissions, UserMessageFilesPermissions
from chat.api.v1.schemas.messages import ListMessagesSchema, UpdateMessageSchema, PaginatedListMessagesSchema
from chat.api.v1.selectors.messages import get_messages_db_query
from chat.models import Message, MessagePhoto
from chat.services.messages import MessagesService, MessagesFilesServices
from chat.websockets.chat import WebSocketConnection, chat_rooms_websocket_manager
from core.database.repository import SQLAlchemyCRUDRepository
from core.dependencies import EventPublisher, EventReceiver, get_paginator
from core.services.files import FilesService
from mixins.schemas import FilesSchema

router = APIRouter()


@router.websocket('/chat_rooms/{chat_room_id}/chat')
async def chat_websocket_endpoint(
        chat_room_id: int,
        websocket: WebSocket,
        request_user: User = Depends(chat_dependencies.get_request_user),
        db_session: AsyncSession = Depends(),
        event_receiver: EventReceiver = Depends(),
        chat_rooms_retrieve_service=Depends(get_chat_rooms_retrieve_service),
):
    db_repository = SQLAlchemyCRUDRepository(Message, db_session)
    permissions = UserChatRoomMessagingPermissions(request_user, chat_room_id, db_repository)
    try:
        await permissions.check_permissions()
    except HTTPException:
        return await websocket.close()
    websocket_connection = WebSocketConnection(websocket, request_user)
    await chat_rooms_websocket_manager.connect(websocket_connection, event_receiver, chat_rooms_retrieve_service)
    try:
        await websocket.receive()
        raise WebSocketDisconnect
    except WebSocketDisconnect:
        await chat_rooms_websocket_manager.disconnect(websocket_connection)


@router.get('/chat_rooms/{chat_room_id}/messages', response_model=PaginatedListMessagesSchema)
async def list_messages_view(
        chat_room_id: int,
        request: Request,
        db_session: AsyncSession = Depends(),
        filterset=Depends(get_messages_filterset),
        paginator=Depends(get_paginator),
):
    db_repository = SQLAlchemyCRUDRepository(Message, db_session)
    return await paginator.paginate(
        filterset.filter_db_query(get_messages_db_query(request, chat_room_id)),
        db_repository
    )


@router.post('/chat_rooms/{chat_room_id}/messages', response_model=ListMessagesSchema)
async def create_message_view(
        chat_room_id: int,
        request: Request,
        text: str = Form(...),
        files: Optional[Tuple[UploadFile]] = None,
        request_user: User = Depends(),
        db_session: AsyncSession = Depends(),
        event_publisher: EventPublisher = Depends(),
):
    db_repository = SQLAlchemyCRUDRepository(Message, db_session)
    await UserChatRoomMessagingPermissions(
        request_user=request_user,
        chat_room_id=chat_room_id,
        db_repository=db_repository,
        request=request,
    ).check_permissions()
    files_service = FilesService(db_repository, MessagePhoto)
    return await MessagesService(db_repository, chat_room_id, event_publisher, files_service).create_message(
        text, files=files, author_id=request_user.id,
    )


@router.patch('/chat_rooms/{chat_room_id}/messages/{message_id}', response_model=ListMessagesSchema)
async def update_message_view(
        chat_room_id: int,
        message_id: int,
        request: Request,
        message_data: UpdateMessageSchema,
        request_user: User = Depends(),
        db_session: AsyncSession = Depends(),
        event_publisher: EventPublisher = Depends(),
):
    db_repository = SQLAlchemyCRUDRepository(Message, db_session)
    await UserChatRoomMessagingPermissions(
        request_user=request_user,
        chat_room_id=chat_room_id,
        db_repository=db_repository,
        request=request,
        message_ids=(message_id,),
    ).check_permissions()
    db_repository.db_query = get_messages_db_query(request, chat_room_id)
    message = await db_repository.get_one(Message.id == message_id)
    return await MessagesService(db_repository, chat_room_id, event_publisher).update_message(
        message, **message_data.dict(exclude_unset=True)
    )


@router.delete('/chat_rooms/{chat_room_id}/messages')
async def delete_messages_view(
        chat_room_id: int,
        request: Request,
        message_ids: tuple[int] = Query(...),
        request_user: User = Depends(),
        db_session: AsyncSession = Depends(),
        event_publisher: EventPublisher = Depends(),
):
    db_repository = SQLAlchemyCRUDRepository(Message, db_session)
    await UserChatRoomMessagingPermissions(
        request_user=request_user,
        chat_room_id=chat_room_id,
        db_repository=db_repository,
        request=request,
        message_ids=message_ids,
    ).check_permissions()
    await MessagesService(db_repository, chat_room_id, event_publisher).delete_messages(message_ids)
    return {'detail': 'success'}


@router.patch('/message/{message_id}/message_files/{message_file_id}', response_model=FilesSchema)
async def replace_message_photo(
        message_id: int,
        message_file_id: int,
        file: UploadFile,
        db_session: AsyncSession = Depends(),
        request_user: Optional[User] = Depends(),
        event_publisher: EventPublisher = Depends(),
) -> dict:
    db_repository = SQLAlchemyCRUDRepository(MessagePhoto, db_session)
    await UserMessageFilesPermissions(request_user, message_file_id, db_repository).check_permissions()
    return await MessagesFilesServices(
        message_id,
        message_file_id,
        db_repository,
        event_publisher
    ).change_message_file(file)


@router.delete('/message/{message_id}/message_files/{message_file_id}')
async def delete_message_photo(
        message_id: int,
        message_file_id: int,
        db_session: AsyncSession = Depends(),
        request_user: Optional[User] = Depends(),
        event_publisher: EventPublisher = Depends(),
) -> dict:
    db_repository = SQLAlchemyCRUDRepository(MessagePhoto, db_session)
    await UserMessageFilesPermissions(request_user, message_file_id, db_repository).check_permissions()
    await MessagesFilesServices(message_id, message_file_id, db_repository, event_publisher).delete_message_file()
    return {'status': 'success'}
