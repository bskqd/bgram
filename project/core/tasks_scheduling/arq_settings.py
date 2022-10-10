import os

from arq.connections import RedisSettings, create_pool, ArqRedis
from dotenv import load_dotenv

load_dotenv()

ARQ_REDIS_URL = os.getenv('ARQ_REDIS_URL')

arq_redis_settings = RedisSettings.from_dsn(ARQ_REDIS_URL)


async def create_arq_redis_pool() -> ArqRedis:
    return await create_pool(arq_redis_settings)
