import asyncio

from celery import Celery
from celery.signals import worker_shutdown
from core.database.base import provide_db_sessionmaker

bgram_celery_app = Celery('bgram_celery_app')

bgram_celery_app.config_from_object('core.celery.celeryconfig')

bgram_celery_app.autodiscover_tasks()


@bgram_celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    pass


@worker_shutdown.connect()
def worker_shutdown_handler(*args, **kwargs):
    provide_db_sessionmaker().close_all()


@bgram_celery_app.task
async def test():
    await asyncio.sleep(5)
    return '=========HELLO========'
