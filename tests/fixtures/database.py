import pytest_asyncio
from core.database.base import provide_db_engine, provide_db_sessionmaker
from sqlalchemy import event

__all__ = ['db_session']


@pytest_asyncio.fixture()
async def db_session():
    connection = await provide_db_engine().connect()
    transaction = await connection.begin()
    session = provide_db_sessionmaker()(bind=connection)
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
