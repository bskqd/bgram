from fastapi import APIRouter

from accounts.api.v1.routers import users, authorization

router = APIRouter()

router.include_router(authorization.router)
router.include_router(users.router)
