from django.db import models

from django_admin.models import BaseCachedModel

from .constants import SAVED_QUERY_BUILDERS_CACHE_PREFIX


class SavedQueryBuilder(BaseCachedModel):
    CACHE_KEY_PREFIX = SAVED_QUERY_BUILDERS_CACHE_PREFIX

    name = models.CharField(max_length=100, unique=True, help_text='The name of the query')
    query = models.JSONField(verbose_name='query')
