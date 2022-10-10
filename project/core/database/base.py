from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.dependencies.providers import settings_provider

engine = create_async_engine(settings_provider().DATABASE_URL)


async def create_sessionmaker() -> sessionmaker:
    return sessionmaker(engine, autoflush=False, expire_on_commit=False, class_=AsyncSession)


DatabaseSession = sessionmaker(engine, autoflush=False, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()
