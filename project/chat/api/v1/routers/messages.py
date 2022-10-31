import asyncio
from datetime import datetime
from typing import Optional

from accounts.models import User
from chat.api.filters.messages import MessagesFilterSetABC
from chat.api.pagination.messages import MessagesPaginatorABC
from chat.api.permissions.messages import UserChatRoomMessagingPermissions, UserMessageFilesPermissions
from chat.api.v1.schemas.messages import ListMessagesSchema, PaginatedListMessagesSchema, UpdateMessageSchema
from chat.constants.messages import MessagesTypeEnum
from chat.database.repository.messages import MessageFilesDatabaseRepositoryABC, MessagesDatabaseRepositoryABC
from chat.database.selectors.messages import get_message_file_db_query, get_messages_with_chat_room_id_db_query
from chat.dependencies import chat as chat_dependencies
from chat.models import Message, MessageFile
from chat.services.chat_rooms import ChatRoomsRetrieveServiceABC
from chat.services.messages import (
    MessageFilesServiceABC,
    MessagesCreateUpdateDeleteServiceABC,
    MessagesRetrieveServiceABC,
)
from chat.websockets.chat import ChatRoomsWebSocketConnectionManager, WebSocketConnection
from core.dependencies.providers import EventReceiver
from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, UploadFile, WebSocket
from mixins.schemas import FilesSchema

router = APIRouter()


@router.websocket('/chat_rooms/{chat_room_id}/chat')
async def chat_websocket_endpoint(
    chat_room_id: int,
    websocket: WebSocket,
    request_user: User = Depends(chat_dependencies.get_request_user),
    messages_db_repository: MessagesDatabaseRepositoryABC = Depends(),
    event_receiver: EventReceiver = Depends(),
    chat_rooms_retrieve_service: ChatRoomsRetrieveServiceABC = Depends(),
):
    permissions = UserChatRoomMessagingPermissions(request_user, chat_room_id, messages_db_repository)
    try:
        await permissions.check_permissions()
    except HTTPException:
        return await websocket.close()
    websocket_connection = WebSocketConnection(websocket, request_user)
    chat_rooms_websocket_manager = ChatRoomsWebSocketConnectionManager(websocket_connection, event_receiver)
    await chat_rooms_websocket_manager.accept_connection()
    try:
        await asyncio.wait(
            [
                chat_rooms_websocket_manager.receive_messages(chat_rooms_retrieve_service),
                websocket.receive(),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )
    finally:
        await chat_rooms_websocket_manager.disconnect()


@router.get('/chat_rooms/{chat_room_id}/messages', response_model=PaginatedListMessagesSchema)
async def list_messages_view(
    chat_room_id: int,
    request: Request,
    filterset: MessagesFilterSetABC = Depends(),
    paginator: MessagesPaginatorABC = Depends(),
):
    return await paginator.paginate(
        filterset.filter_db_query(
            get_messages_with_chat_room_id_db_query(
                request,
                chat_room_id,
                Message.message_type == MessagesTypeEnum.PRIMARY.value,
            ),
        ),
    )


@router.get('/chat_rooms/{chat_room_id}/scheduled_messages', response_model=PaginatedListMessagesSchema)
async def list_scheduled_messages_view(
    chat_room_id: int,
    request: Request,
    request_user: User = Depends(),
    filterset: MessagesFilterSetABC = Depends(),
    paginator: MessagesPaginatorABC = Depends(),
):
    return await paginator.paginate(
        filterset.filter_db_query(
            get_messages_with_chat_room_id_db_query(
                request,
                chat_room_id,
                User.id == request_user.id,
                Message.message_type == MessagesTypeEnum.SCHEDULED.value,
            ),
        ),
    )


@router.post('/chat_rooms/{chat_room_id}/messages', response_model=ListMessagesSchema)
async def create_message_view(
    chat_room_id: int,
    request: Request,
    text: str = Form(...),
    message_type: str = Form(...),
    scheduled_at: Optional[str] = Form(None),
    files: Optional[list[UploadFile]] = None,
    request_user: User = Depends(),
    messages_db_repository: MessagesDatabaseRepositoryABC = Depends(),
    messages_create_update_delete_service: MessagesCreateUpdateDeleteServiceABC = Depends(),
):
    await UserChatRoomMessagingPermissions(
        request_user=request_user,
        chat_room_id=chat_room_id,
        db_repository=messages_db_repository,
        request=request,
    ).check_permissions()
    if message_type == MessagesTypeEnum.SCHEDULED:
        return await messages_create_update_delete_service.create_scheduled_message(
            text,
            files=files,
            author_id=request_user.id,
            scheduled_at=datetime.strptime(scheduled_at, '%d.%m.%Y %H:%M'),
        )
    return await messages_create_update_delete_service.create_message(text, files=files, author_id=request_user.id)


@router.patch('/chat_rooms/{chat_room_id}/messages/{message_id}', response_model=ListMessagesSchema)
async def update_message_view(
    chat_room_id: int,
    message_id: int,
    request: Request,
    message_data: UpdateMessageSchema,
    request_user: User = Depends(),
    messages_db_repository: MessagesDatabaseRepositoryABC = Depends(),
    messages_create_update_delete_service: MessagesCreateUpdateDeleteServiceABC = Depends(),
    messages_retrieve_service: MessagesRetrieveServiceABC = Depends(),
):
    await UserChatRoomMessagingPermissions(
        request_user=request_user,
        chat_room_id=chat_room_id,
        db_repository=messages_db_repository,
        request=request,
        message_ids=(message_id,),
    ).check_permissions()
    message = await messages_retrieve_service.get_one_message(
        Message.id == message_id,
        db_query=get_messages_with_chat_room_id_db_query(
            request,
            chat_room_id,
            Message.message_type.in_(
                (MessagesTypeEnum.PRIMARY.value, MessagesTypeEnum.SCHEDULED.value),
            ),
        ),
    )
    if message.message_type == MessagesTypeEnum.SCHEDULED:
        await messages_create_update_delete_service.update_scheduled_message(
            message, **message_data.dict(exclude_unset=True)
        )
    return await messages_create_update_delete_service.update_message(message, **message_data.dict(exclude_unset=True))


@router.delete('/chat_rooms/{chat_room_id}/messages')
async def delete_messages_view(
    chat_room_id: int,
    request: Request,
    message_ids: tuple[int, ...] = Query(...),
    message_type: str = Query(...),
    request_user: User = Depends(),
    messages_db_repository: MessagesDatabaseRepositoryABC = Depends(),
    messages_create_update_delete_service: MessagesCreateUpdateDeleteServiceABC = Depends(),
):
    await UserChatRoomMessagingPermissions(
        request_user=request_user,
        chat_room_id=chat_room_id,
        db_repository=messages_db_repository,
        request=request,
        message_ids=message_ids,
    ).check_permissions()
    if message_type == MessagesTypeEnum.SCHEDULED:
        await messages_create_update_delete_service.delete_scheduled_messages(message_ids)
    await messages_create_update_delete_service.delete_messages(message_ids)
    return {'detail': 'success'}


@router.patch('/message/{message_id}/message_files/{message_file_id}', response_model=FilesSchema)
async def replace_message_file(
    message_file_id: int,
    file: UploadFile,
    request_user: User = Depends(),
    message_files_db_repository: MessageFilesDatabaseRepositoryABC = Depends(),
    message_files_service: MessageFilesServiceABC = Depends(),
) -> dict:
    await UserMessageFilesPermissions(
        request_user,
        message_file_id,
        message_files_db_repository,
    ).check_permissions()
    message_file = await message_files_service.get_one_message_file(
        db_query=get_message_file_db_query(MessageFile.id == message_file_id),
    )
    if message_file.message.message_type == MessagesTypeEnum.SCHEDULED:
        return await message_files_service.change_scheduled_message_file(file, message_file)
    return await message_files_service.change_message_file(file, message_file)


@router.delete('/message/{message_id}/message_files/{message_file_id}')
async def delete_message_file(
    message_file_id: int,
    request_user: User = Depends(),
    message_files_db_repository: MessageFilesDatabaseRepositoryABC = Depends(),
    message_files_service: MessageFilesServiceABC = Depends(),
) -> dict:
    await UserMessageFilesPermissions(request_user, message_file_id, message_files_db_repository).check_permissions()
    message_file = await message_files_service.get_one_message_file(
        db_query=get_message_file_db_query(MessageFile.id == message_file_id),
    )
    if message_file.message.message_type == MessagesTypeEnum.SCHEDULED:
        await message_files_service.delete_scheduled_message_file(message_file)
        return {'status': 'success'}
    await message_files_service.delete_message_file(message_file)
    return {'status': 'success'}
