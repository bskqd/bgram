import asyncio
import os
import time

import pytest_asyncio
from dotenv import load_dotenv

from project.core.database.base import provide_db_engine
from project.core.database.models import *  # noqa: F401, F403
from tests.fixtures import *  # noqa: F401, F403

load_dotenv()

if os.environ.get('ENVIRONMENT') != 'TEST':
    raise Exception('Production env is loaded instead of the test one')


async def init_models():
    metadata = get_metadata()  # noqa: F405
    async with provide_db_engine().begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)


# waiting for db to be ready to accept connections
counter = 0
while counter <= 3:
    try:
        asyncio.run(init_models())
    except Exception:
        time.sleep(5)
        counter += 1


@pytest_asyncio.fixture(scope='session', autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
