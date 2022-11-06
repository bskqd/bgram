import abc
import os
from pathlib import Path

from core.contrib import redis as redis_contrib
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig
from passlib.context import CryptContext
from pydantic import BaseSettings

load_dotenv()


class SettingsABC(abc.ABC):
    BASE_DIR = str

    DATABASE_URL: str
    HOST_DOMAIN: str

    DATETIME_INPUT_OUTPUT_FORMAT: str

    CONFIRMATION_TOKEN_VALID_HOURS: int
    MAIL_CONFIG: ConnectionConfig

    JWT_TOKEN_TYPE_NAME: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int
    JWT_ACCESS_TOKEN_TYPE: str
    JWT_REFRESH_TOKEN_TYPE: str

    REDIS_HOST_URL: str

    PWD_CONTEXT: CryptContext

    MEDIA_PATH: str
    MEDIA_URL: str


class Settings(BaseSettings, SettingsABC):
    BASE_DIR = Path(__file__).resolve().parent.parent

    DATABASE_URL: str = os.getenv('DATABASE_URL')
    HOST_DOMAIN: str = os.getenv('HOST_DOMAIN', 'http://127.0.0.1:8000')

    DATETIME_INPUT_OUTPUT_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    CONFIRMATION_TOKEN_VALID_HOURS: int = 24
    MAIL_CONFIG: ConnectionConfig = ConnectionConfig(
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
        MAIL_FROM=os.getenv('MAIL_USERNAME'),
        MAIL_PORT=587,
        MAIL_SERVER=os.getenv('MAIL_SERVER'),
        MAIL_FROM_NAME='Bgram services',
        MAIL_TLS=True,
        MAIL_SSL=False,
        USE_CREDENTIALS=True,
        TEMPLATE_FOLDER=os.path.join(BASE_DIR, 'notifications', 'templates', 'email'),
    )

    JWT_TOKEN_TYPE_NAME: str = 'Bearer'
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY')
    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440
    JWT_ACCESS_TOKEN_TYPE: str = 'access_token'
    JWT_REFRESH_TOKEN_TYPE: str = 'refresh_token'

    REDIS_HOST_URL: str = redis_contrib.REDIS_HOST_URL

    PWD_CONTEXT: CryptContext = CryptContext(schemes=['bcrypt'], deprecated='auto')

    MEDIA_PATH: str = os.getenv('MEDIA_PATH')
    MEDIA_URL: str = 'media'
