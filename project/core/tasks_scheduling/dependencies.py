import abc
from dataclasses import dataclass
from typing import Optional

from arq import ArqRedis
from arq.jobs import Job
from core.tasks_scheduling.constants import TASKS_SCHEDULING_QUEUE
from fastapi import Request


@dataclass
class JobResult:
    job_id: str


class TasksSchedulerABC(abc.ABC):
    @abc.abstractmethod
    async def enqueue_job(self, func: str, *func_args, **kwargs) -> Optional[JobResult]:
        pass

    @abc.abstractmethod
    async def cancel_job(self, job_id: str) -> bool:
        pass


class TasksScheduler(TasksSchedulerABC):
    def __init__(self, connection_pool: ArqRedis):
        self._connection_pool = connection_pool

    async def enqueue_job(self, func: str, *func_args, **kwargs) -> Optional[JobResult]:
        return await self._connection_pool.enqueue_job(func, *func_args, **kwargs)

    async def cancel_job(self, job_id: str) -> bool:
        job = Job(job_id, self._connection_pool, _queue_name=TASKS_SCHEDULING_QUEUE)
        return await job.abort(timeout=1)


class TaskSchedulerDependenciesOverrides:
    @staticmethod
    async def get_tasks_scheduler(request: Request) -> TasksSchedulerABC:
        return TasksScheduler(request.app.state.arq_redis_pool)

    def override_dependencies(self) -> dict:
        return {
            TasksSchedulerABC: self.get_tasks_scheduler,
        }
