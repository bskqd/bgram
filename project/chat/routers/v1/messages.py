import aioredis
from fastapi import WebSocket, APIRouter, WebSocketDisconnect, Depends

from accounts.models import User
from chat.dependencies.messages import get_request_user
from core.config import settings
from core.services import websockets as websockets_services

router = APIRouter()

messages_websocket_manager = websockets_services.WebSocketConnectionManager()
messages_redis_db = aioredis.from_url(settings.MESSAGES_REDIS_DB_URL)


@router.websocket("/messages")
async def messages_websocket_endpoint(websocket: WebSocket, user: User = Depends(get_request_user)):
    await messages_websocket_manager.connect(websocket)
    await messages_redis_db.hset()
    try:
        while True:
            data = await websocket.receive_json()
            await messages_websocket_manager.broadcast({'Client says': data})
    except WebSocketDisconnect:
        messages_websocket_manager.disconnect(websocket)
        await messages_websocket_manager.broadcast({'Client': 'has left the chat'})
