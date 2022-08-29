import abc
import json
from datetime import datetime

from fastapi import Depends

from core.dependencies import EventPublisher


class TaskSchedulerABC(abc.ABC):
    @abc.abstractmethod
    async def add_task(self, task_name: str, trigger_datetime: datetime):
        pass


class TaskScheduler:
    def __init__(self, event_publisher: EventPublisher):
        self.event_publisher = event_publisher

    async def add_task(self, task_name: str, trigger_datetime: datetime):
        await self.event_publisher.publish(
            'celery_tasks_scheduler',
            json.dumps(
                {
                    'task_name': task_name,
                    'trigger_datetime': trigger_datetime.strftime('%Y.%m.$d %H:%M:%S'),
                },
            ),
        )


class TaskSchedulerDependenciesProvider:
    @staticmethod
    async def get_tasks_scheduler(event_publisher: EventPublisher = Depends()):
        return TaskScheduler(event_publisher)
