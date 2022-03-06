import multiprocessing

bind = "0.0.0.0:8000"
worker_class = 'uvicorn.workers.UvicornWorker'
workers = multiprocessing.cpu_count() * 2 + 1
reload = True

accesslog = '-'
access_log_format = '%(t)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
