from fastapi import APIRouter

from accounts.api.v1.routers.urls import router as accounts_router_v1
from chat.api.v1.routers.urls import router as chat_router_v1

router = APIRouter()

router.include_router(accounts_router_v1, prefix='/accounts')
router.include_router(chat_router_v1, prefix='/test_chat')
