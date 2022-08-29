import json
from datetime import datetime

import redis
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from dotenv import load_dotenv
from pytz import utc

from core.celery.celery_app import bgram_celery_app
from core.config import settings

load_dotenv()


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


def main():
    bgram_scheduler = initialize_scheduler()
    bgram_scheduler.start()
    redis_client = redis.from_url(settings.REDIS_HOST_URL)
    event_receiver = redis_client.pubsub()
    event_receiver.subscribe('celery_tasks_scheduler')
    try:
        for message in event_receiver.listen():
            if message and message.get('type') != 'subscribe' and (data := message.get('data')):
                data = json.loads(data.decode('utf-8'))
                bgram_scheduler.add_job(
                    celery_task,
                    DateTrigger(
                        run_date=datetime.strptime(data.get('trigger_datetime'), '%Y.%m.$d %H:%M:%S'),
                        timezone=utc,
                    ),
                    name=data.get('task_name'),
                )
    except Exception as e:
        print(e)
    finally:
        event_receiver.unsubscribe()
        bgram_scheduler.shutdown()


def celery_task():
    """
    Empty function to use when the scheduler schedules a celery task.
    """
    pass


def initialize_scheduler():
    jobstores = {'default': SQLAlchemyJobStore(url=settings.SYNC_DATABASE_URL)}
    executors = {'default': CeleryPoolExecutor()}
    job_defaults = {'coalesce': False, 'max_instances': 3}
    return BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)


if __name__ == '__main__':
    main()
