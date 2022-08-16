import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

bgram_celery_app = Celery(
    'bgram_celery_app',
    broker=os.getenv('CELERY_BROKER_URL'),
    backend=os.getenv('CELERY_BROKER_URL'),
)
