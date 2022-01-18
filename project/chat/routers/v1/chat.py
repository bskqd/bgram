from fastapi import WebSocket, APIRouter, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session

from accounts.models import User
from chat.dependencies.chat import get_request_user
from chat.permissions.chat import UserChatRoomMessagingPermissions
from chat.services.chat import WebSocketConnection, chat_rooms_websocket_manager
from mixins import dependencies as mixins_dependencies

router = APIRouter()


@router.websocket('/chat_rooms/{chat_room_id}/chat')
async def chat_websocket_endpoint(
        chat_room_id: int,
        websocket: WebSocket,
        request_user: User = Depends(get_request_user),
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
