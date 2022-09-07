from dataclasses import dataclass
from typing import Optional

from arq import create_pool, ArqRedis

from core.tasks_scheduling.arq_settings import arq_redis_settings


@dataclass
class JobResult:
    job_id: str


class TasksScheduler:
    async def enqueue_job(self, func: str, *func_args, **kwargs) -> Optional[JobResult]:
        pass


class TaskSchedulerDependenciesProvider:
    def __init__(self, arq_redis_connection_pool: Optional[ArqRedis] = None):
        self.arq_redis_connection_pool = arq_redis_connection_pool

    async def get_tasks_scheduler(self) -> TasksScheduler:
        if not self.arq_redis_connection_pool:
            await self.initialize_arq_redis_pool()
        return self.arq_redis_connection_pool

    async def initialize_arq_redis_pool(self):
        self.arq_redis_connection_pool = await create_pool(arq_redis_settings)
