import pytest_asyncio
from sqlalchemy import event

from core.database.base import db_engine, db_sessionmaker

__all__ = ['db_session']


@pytest_asyncio.fixture()
async def db_session():
    connection = await db_engine().connect()
    transaction = await connection.begin()
    session = db_sessionmaker()(bind=connection)
    nested = await connection.begin_nested()  # Begin a nested transaction (using SAVEPOINT).

    # If the application code calls session.commit, it will end the nested transaction.
    # Need to start a new one when that happens.
    @event.listens_for(session.sync_session, 'after_transaction_end')
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.sync_connection.begin_nested()

    yield session

    # Rollback the overall transaction, restoring the state before the test ran.
    await session.close()
    await transaction.rollback()
    await connection.close()
