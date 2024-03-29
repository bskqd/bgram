import asyncio
from typing import Optional

from arq import Worker
from chat.async_tasks.messages import send_scheduled_message
from core.celery.celery_app import bgram_celery_app
from core.contrib.redis import RedisClientProvider
from core.database.base import provide_db_sessionmaker
from core.tasks_scheduling.arq_settings import arq_redis_settings
from core.tasks_scheduling.constants import TASKS_SCHEDULING_QUEUE


async def execute_task_in_background(job_context: dict, task_name: str, task_kwargs: Optional[dict] = None) -> bool:
    task_kwargs = task_kwargs if task_kwargs is not None else {}
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, bgram_celery_app.send_task, task_name, None, task_kwargs)
    return True


async def on_shutdown(context: dict):
    provide_db_sessionmaker().close_all()
    await RedisClientProvider.provide_redis_client().close()


class TaskSchedulingWorkerSettings(Worker):
    functions = [execute_task_in_background, send_scheduled_message]
    queue_name = TASKS_SCHEDULING_QUEUE
    redis_settings = arq_redis_settings
    on_shutdown = on_shutdown
    allow_abort_jobs = True
