import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()


celery = Celery('bgram_celery_app')
celery.conf.broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
celery.conf.result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
