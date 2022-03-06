from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from core.config import settings
from core.middleware.authentication import JWTAuthenticationMiddleware
from routers import v1

app = FastAPI()

app.add_middleware(JWTAuthenticationMiddleware)

app.mount(f'/{settings.MEDIA_URL}', StaticFiles(directory=settings.MEDIA_PATH), name='media')

app.include_router(v1.router, prefix='/api/v1')
