from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

from core.celery.celery_app import bgram_celery_app
from core.config import settings


def celery_task():
    """
    Empty function to use when the scheduler schedules a celery task.
    """
    pass


class CeleryPoolExecutor(ThreadPoolExecutor):
    """
    A threaded pool executor that will dispatch celery tasks instead running the tasks itself.
    """

    def _do_submit_job(self, job: Job, run_times: int) -> None:
        try:
            bgram_celery_app.send_task(job.name, args=job.args, kwargs=job.kwargs)
            self._run_job_success(job.id, [])
        except Exception as e:
            self._run_job_error(job.id, e, [])


jobstores = {'default': SQLAlchemyJobStore(url=settings.SYNC_DATABASE_URL)}
executors = {'default': CeleryPoolExecutor()}
job_defaults = {'coalesce': False, 'max_instances': 3}
bgram_scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)


def run_scheduler():
    bgram_scheduler.start()
