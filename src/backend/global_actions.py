from typing import Callable

from django.http import HttpRequest
from rest_framework.response import Response

from backend.settings.base import IS_DEMO_MODE
from django_admin.actions import copy_demo_model, delete_listview

# Register admin actions here
ACTION_FUNCS: dict[str, Callable[[HttpRequest, str, str, list[str]], Response]]  = {
    'delete': delete_listview,
}

if IS_DEMO_MODE:
    ACTION_FUNCS['copy_demo_model'] = copy_demo_model