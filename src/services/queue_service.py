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
        queue = {'fields': [], 'name': q.get('name')}
        queue['fields'].append({'label': 'Queued Jobs', 'value': q.get('jobs'), 'field': 'jobs'})
        queue['fields'].append({'label': 'Oldest Queued Job', 'value': q.get('oldest_job_timestamp'), 'field': 'oldest_job_timestamp'})
        queue['fields'].append({'label': 'Started Jobs', 'value': q.get('started_jobs'), 'field': 'started_jobs'})
        queue['fields'].append({'label': 'Workers', 'value': q.get('workers'), 'field': 'workers'})
        queue['fields'].append({'label': 'Finished Jobs', 'value': q.get('finished_jobs'), 'field': 'finished_jobs'})
        queue['fields'].append({'label': 'Deferred Jobs', 'value': q.get('deferred_jobs'), 'field': 'deferred_jobs'})
        queue['fields'].append({'label': 'Failed Jobs', 'value': q.get('failed_jobs'), 'field': 'failed_jobs'})
        queue['fields'].append({'label': 'Scheduled Jobs', 'value': q.get('scheduled_jobs'), 'field': 'scheduled_jobs'})
        queue['fields'].append({'label': 'Host', 'value': q.get('connection_kwargs').get('host'), 'field': 'host'})
        queue['fields'].append({'label': 'Port', 'value': q.get('connection_kwargs').get('port'), 'field': 'port'})
        queue['fields'].append({'label': 'Scheduler PID', 'value': q.get('scheduler_pid'), 'field': 'scheduler_pid'})
        
        queues.append(queue)

    return queues