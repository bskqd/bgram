from accounts.api.v1.routers import authorization, users
from fastapi import APIRouter

router = APIRouter()

router.include_router(authorization.router)
router.include_router(users.router)
