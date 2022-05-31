import os

import aioredis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST_URL = os.getenv('REDIS_HOST_URL')

redis_client = aioredis.from_url(REDIS_HOST_URL)
