from core.celery.celery_app import bgram_celery_app

__all__ = ['test']


@bgram_celery_app.task
def test(arg: int):
    return arg
