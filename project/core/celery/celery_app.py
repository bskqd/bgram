from celery import Celery
from dotenv import load_dotenv

load_dotenv()

bgram_celery_app = Celery('bgram_celery_app')

bgram_celery_app.config_from_object('core.celery.celeryconfig')

bgram_celery_app.autodiscover_tasks(['core.celery'])


@bgram_celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    pass
