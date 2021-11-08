from fastapi import APIRouter

from accounts.routers.v1.api import router as accounts_router_v1

router = APIRouter()

router.include_router(accounts_router_v1, prefix='/accounts')
