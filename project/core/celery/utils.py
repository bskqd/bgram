import asyncio
import functools


def run_task_asynchronously(func):
    @functools.wraps(func)
    def _run_task_asynchronously(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return _run_task_asynchronously
