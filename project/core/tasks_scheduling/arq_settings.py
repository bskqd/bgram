import os

from arq.connections import RedisSettings
from dotenv import load_dotenv

load_dotenv()

ARQ_REDIS_URL = os.getenv('ARQ_REDIS_URL')

arq_redis_settings = RedisSettings.from_dsn(ARQ_REDIS_URL)
