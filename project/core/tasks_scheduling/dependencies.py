from dataclasses import dataclass
from typing import Optional

from fastapi import Request


@dataclass
class JobResult:
    job_id: str


class TasksScheduler:
    async def enqueue_job(self, func: str, *func_args, **kwargs) -> Optional[JobResult]:
        pass


class TaskSchedulerDependenciesOverrides:
    @staticmethod
    async def get_tasks_scheduler(request: Request) -> TasksScheduler:
        return request.app.state.arq_redis_pool

    def override_dependencies(self) -> dict:
        return {
            TasksScheduler: self.get_tasks_scheduler,
        }
