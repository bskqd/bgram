from accounts.api.v1.routers import authentication, users
from fastapi import APIRouter

router = APIRouter()

router.include_router(authentication.router)
router.include_router(users.router)
