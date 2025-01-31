from typing import Any, Callable

import django_rq
import httpx

from backend.settings.base import APP_MODE, DOMAIN, PROTOCOL, RQ_API_TOKEN, DjangoSettings


def enqueue(func: Callable, *args: Any, **kwargs: Any) -> None:
    """
        Enqueues task to django rq. 
    """
    if APP_MODE == DjangoSettings.TEST:
        return
    
    django_rq.enqueue(func, *args, **kwargs)


def get_queue_list() -> list[dict]:
    response = httpx.get(f'{PROTOCOL}://{DOMAIN}/django-rq/stats.json/{RQ_API_TOKEN}')
    data = response.json()

    queues = []
    for q in data.get('queues'):
        queue = {}
        queue['name'] = q.get('name')
        queue['queued_jobs'] = q.get('jobs')
        queue['oldest_queued_job'] = q.get('oldest_job_timestamp')
        queue['started_jobs'] = q.get('started_jobs')
        queue['workers'] = q.get('workers')
        queue['finished_jobs'] = q.get('finished_jobs')
        queue['deferred_jobs'] = q.get('deferred_jobs')
        queue['failed_jobs'] = q.get('failed_jobs')
        queue['scheduled_jobs'] = q.get('scheduled_jobs')
        queue['host'] = q.get('connection_kwargs').get('host')
        queue['port'] = q.get('connection_kwargs').get('port')
        queue['scheduler_pid'] = q.get('scheduler_pid')
        
        queues.append(queue)

    return queues