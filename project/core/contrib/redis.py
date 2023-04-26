import os

from dotenv import load_dotenv
from redis import asyncio as aioredis

load_dotenv()

REDIS_HOST_URL = os.getenv('REDIS_HOST_URL')


class RedisClientProvider:
    __redis_client = aioredis.from_url(REDIS_HOST_URL)

    @classmethod
    def provide_redis_client(cls) -> aioredis.Redis:
        return cls.__redis_client
