from typing import Optional, Tuple

from fastapi import (
    APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, Form, Request, Query,
)

from accounts.models import User
from chat.api.dependencies import chat as chat_dependencies
from chat.api.dependencies.chat_rooms import get_chat_rooms_retrieve_service
from chat.api.dependencies.messages import (
    get_messages_filterset, get_messages_db_repository, get_messages_create_update_delete_service,
    get_messages_retrieve_service, get_message_files_service
)
from chat.api.permissions.messages import UserChatRoomMessagingPermissions, UserMessageFilesPermissions
from chat.api.v1.schemas.messages import ListMessagesSchema, UpdateMessageSchema, PaginatedListMessagesSchema
from chat.api.v1.selectors.messages import get_messages_db_query
from chat.models import Message
from chat.websockets.chat import WebSocketConnection, chat_rooms_websocket_manager
from core.dependencies import EventReceiver, get_paginator
from mixins.schemas import FilesSchema

router = APIRouter()


@router.websocket('/chat_rooms/{chat_room_id}/chat')
async def chat_websocket_endpoint(
        chat_room_id: int,
        websocket: WebSocket,
        request_user: User = Depends(chat_dependencies.get_request_user),
        messages_db_repository=Depends(get_messages_db_repository),
        event_receiver: EventReceiver = Depends(),
        chat_rooms_retrieve_service=Depends(get_chat_rooms_retrieve_service),
):
    permissions = UserChatRoomMessagingPermissions(request_user, chat_room_id, messages_db_repository)
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
        filterset=Depends(get_messages_filterset),
        paginator=Depends(get_paginator),
):
    return await paginator.paginate(filterset.filter_db_query(get_messages_db_query(request, chat_room_id)))


@router.post('/chat_rooms/{chat_room_id}/messages', response_model=ListMessagesSchema)
async def create_message_view(
        chat_room_id: int,
        request: Request,
        text: str = Form(...),
        files: Optional[Tuple[UploadFile]] = None,
        request_user: User = Depends(),
        messages_db_repository=Depends(get_messages_db_repository),
        messages_create_update_delete_service=Depends(get_messages_create_update_delete_service),
):
    await UserChatRoomMessagingPermissions(
        request_user=request_user,
        chat_room_id=chat_room_id,
        db_repository=messages_db_repository,
        request=request,
    ).check_permissions()
    return await messages_create_update_delete_service.create_message(text, files=files, author_id=request_user.id)


@router.patch('/chat_rooms/{chat_room_id}/messages/{message_id}', response_model=ListMessagesSchema)
async def update_message_view(
        chat_room_id: int,
        message_id: int,
        request: Request,
        message_data: UpdateMessageSchema,
        request_user: User = Depends(),
        messages_db_repository=Depends(get_messages_db_repository),
        messages_create_update_delete_service=Depends(get_messages_create_update_delete_service),
        messages_retrieve_service=Depends(get_messages_retrieve_service),
):
    await UserChatRoomMessagingPermissions(
        request_user=request_user,
        chat_room_id=chat_room_id,
        db_repository=messages_db_repository,
        request=request,
        message_ids=(message_id,),
    ).check_permissions()
    message = await messages_retrieve_service.get_one_message(
        Message.id == message_id, db_query=get_messages_db_query(request, chat_room_id)
    )
    return await messages_create_update_delete_service.update_message(message, **message_data.dict(exclude_unset=True))


@router.delete('/chat_rooms/{chat_room_id}/messages')
async def delete_messages_view(
        chat_room_id: int,
        request: Request,
        message_ids: tuple[int] = Query(...),
        request_user: User = Depends(),
        messages_db_repository=Depends(get_messages_db_repository),
        messages_create_update_delete_service=Depends(get_messages_create_update_delete_service),
):
    await UserChatRoomMessagingPermissions(
        request_user=request_user,
        chat_room_id=chat_room_id,
        db_repository=messages_db_repository,
        request=request,
        message_ids=message_ids,
    ).check_permissions()
    await messages_create_update_delete_service.delete_messages(message_ids)
    return {'detail': 'success'}


@router.patch('/message/{message_id}/message_files/{message_file_id}', response_model=FilesSchema)
async def replace_message_photo(
        message_file_id: int,
        file: UploadFile,
        request_user: Optional[User] = Depends(),
        message_files_db_repository=Depends(get_messages_db_repository),
        message_files_service=Depends(get_message_files_service),
) -> dict:
    await UserMessageFilesPermissions(
        request_user,
        message_file_id,
        message_files_db_repository,
    ).check_permissions()
    return message_files_service.change_message_file(file)


@router.delete('/message/{message_id}/message_files/{message_file_id}')
async def delete_message_photo(
        message_file_id: int,
        request_user: Optional[User] = Depends(),
        message_files_db_repository=Depends(get_messages_db_repository),
        message_files_service=Depends(get_message_files_service),
) -> dict:
    await UserMessageFilesPermissions(request_user, message_file_id, message_files_db_repository).check_permissions()
    await message_files_service.delete_message_file()
    return {'status': 'success'}
