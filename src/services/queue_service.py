import logging
from typing import Any, Callable

import django_rq
import httpx
from rq import Queue
from rq.job import Job
from rq.registry import FailedJobRegistry

from backend.settings.base import (
    APP_MODE,
    DOMAIN,
    PROTOCOL,
    RQ_API_TOKEN,
    DjangoSettings,
)

log = logging.getLogger(__name__)


def build_job_dict(job: Job) -> dict:
    return {
        'id': job.id,
        'created_at': job.created_at,
        'started_at': job.started_at,
        'enqueued_at': job.enqueued_at,
        'ended_at': job.ended_at,
        'timeout': job.timeout,
        'ttl': job.ttl,
        'meta': job.meta,
        'callable': job.func_name,
        'args': list(job.args),
        'kwargs': job.kwargs,
        'execution_info': job.exc_info
    }

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

def get_failed_jobs(queue_name: str) -> list[dict]:
    queue = django_rq.get_queue()
    failed_job_registry = FailedJobRegistry(queue=queue)
    failed_job_ids = failed_job_registry.get_job_ids()
    redis_conn = django_rq.get_connection(queue_name)

    jobs = []
    for id in failed_job_ids:
        job = Job.fetch(id, connection=redis_conn)
        obj = build_job_dict(job)
        jobs.append(obj)
    
    return jobs

def get_job(queue_name: str, job_id: str) -> dict:
    redis_conn = django_rq.get_connection(queue_name)
    job = Job.fetch(job_id, connection=redis_conn)
    return build_job_dict(job)

def requeue_job(queue_name: str, job_id: str) -> None:
    redis_conn = django_rq.get_connection(queue_name)

    queue = Queue(queue_name, connection=redis_conn)
    registry = queue.failed_job_registry
    for failed_job_id in registry.get_job_ids():
        if failed_job_id == job_id:
            registry.requeue(job_id)
            break

    log.info(f'Requeued job {job_id} for queue {queue_name}')