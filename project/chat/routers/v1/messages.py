from fastapi import WebSocket, APIRouter, WebSocketDisconnect, Request

from core.services import websockets as websockets_services

router = APIRouter()

messages_websocket_manager = websockets_services.WebSocketConnectionManager()


@router.websocket("/messages")
async def messages_websocket_endpoint(websocket: WebSocket):
    await messages_websocket_manager.connect(websocket)
    await messages_websocket_manager.broadcast({'Client': 'has entered the chat'})
    try:
        while True:
            data = await websocket.receive_json()
            await messages_websocket_manager.send_personal_message(data, websocket)
            await messages_websocket_manager.broadcast({'Client says': data})
    except WebSocketDisconnect:
        messages_websocket_manager.disconnect(websocket)
        await messages_websocket_manager.broadcast({'Client': 'has left the chat'})
