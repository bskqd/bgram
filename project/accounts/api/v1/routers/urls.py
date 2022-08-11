from fastapi import APIRouter

from accounts.api.v1.routers import users, authentication

router = APIRouter()

router.include_router(authentication.router)
router.include_router(users.router)
