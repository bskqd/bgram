import pytest
from core.tasks_scheduling.dependencies import JobResult, TasksSchedulerABC

__all__ = ['tasks_scheduler']


class TestsTasksScheduler(TasksSchedulerABC):
    async def enqueue_job(self, func: str, *func_args, **kwargs) -> JobResult:
        return JobResult(job_id='tests_tasks_scheduler_id')

    async def cancel_job(self, job_id: str) -> bool:
        return True


@pytest.fixture(scope='session', autouse=True)
def tasks_scheduler() -> TasksSchedulerABC:
    return TestsTasksScheduler()
