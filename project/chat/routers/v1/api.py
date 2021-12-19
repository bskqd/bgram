from fastapi import APIRouter

from chat.routers.v1 import chat_room, messages

router = APIRouter()

router.include_router(chat_room.router)
router.include_router(messages.router)
