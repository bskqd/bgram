from fastapi import APIRouter

from chat.routers.v1 import chat_rooms, messages

router = APIRouter()

router.include_router(chat_rooms.router)
router.include_router(messages.router)
