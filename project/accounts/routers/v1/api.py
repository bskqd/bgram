from fastapi import APIRouter

from accounts.routers.v1 import authorization, users

router = APIRouter()

router.include_router(authorization.router)
router.include_router(users.router)
