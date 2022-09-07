from core.celery.celery_app import bgram_celery_app

__all__ = ['send_scheduled_message']


@bgram_celery_app.task
def send_scheduled_message(scheduled_message_id: int):
    # TODO: implement logic
    return scheduled_message_id
