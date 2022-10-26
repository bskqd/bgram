import asyncio

import pytest_asyncio

from project.core.database.base import db_engine
from project.core.database.models import *  # noqa: F401, F403
from tests.fixtures import *  # noqa: F401, F403


async def init_models():
    metadata = get_metadata()  # noqa: F405
    async with db_engine().begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

asyncio.run(init_models())


@pytest_asyncio.fixture(scope='session', autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
