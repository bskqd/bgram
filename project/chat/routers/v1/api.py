from fastapi import APIRouter

from chat.routers.v1 import chat_room

router = APIRouter()

router.include_router(chat_room.router)
