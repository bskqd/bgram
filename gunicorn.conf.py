import multiprocessing

from gunicorn import glogging

bind = '0.0.0.0:8000'
worker_class = 'uvicorn.workers.UvicornWorker'
workers = multiprocessing.cpu_count() * 2 + 1
reload = True
preload = True

accesslog = '-'

logging_format = '%(asctime)s [%(levelname)s] %(message)s'
glogging.Logger.access_fmt = logging_format
glogging.Logger.error_fmt = logging_format
