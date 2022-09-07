from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import settings

engine = create_async_engine(settings.DATABASE_URL)
DatabaseSession = sessionmaker(engine, autoflush=False, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()
