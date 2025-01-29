from typing import Any, Callable

import django_rq

from backend.settings.base import APP_MODE, DjangoSettings


def enqueue(func: Callable, *args: Any, **kwargs: Any) -> None:
    """
        Enqueues task to django rq. 
    """
    if APP_MODE == DjangoSettings.TEST:
        return
    
    django_rq.enqueue(func, *args, **kwargs)