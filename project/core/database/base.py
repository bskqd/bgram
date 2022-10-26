from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import SettingsABC
from core.dependencies.providers import provide_settings


def db_engine(config: SettingsABC = provide_settings()):
    engine = getattr(db_engine, 'engine', None)
    if not engine:
        engine = db_engine.engine = create_async_engine(config.DATABASE_URL)
    return engine


def db_sessionmaker(config: SettingsABC = provide_settings(), create_new: bool = False) -> sessionmaker:
    engine = db_engine(config)
    if create_new:
        return sessionmaker(engine, autoflush=False, expire_on_commit=False, class_=AsyncSession)
    session = getattr(db_sessionmaker, 'session', None)
    if not session:
        session = db_sessionmaker.session = sessionmaker(
            engine, autoflush=False, expire_on_commit=False, class_=AsyncSession,
        )
    return session


Base = declarative_base()
