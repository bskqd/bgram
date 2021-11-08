from database import DatabaseSession


async def db_session() -> DatabaseSession:
    async with (session := DatabaseSession()):
        yield session
