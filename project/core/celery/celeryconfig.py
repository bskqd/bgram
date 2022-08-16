import os

from dotenv import load_dotenv

load_dotenv()

broker_url = os.getenv('CELERY_BROKER_URL')
result_backend = os.getenv('CELERY_BROKER_URL')

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Kiev'
enable_utc = True
