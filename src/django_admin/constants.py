from typing import Literal

LIST_PAGE_COUNT = 20

DASHBOARD_URL_PREFIX = '/dashboard'

PermissionType = Literal["add", "edit", "delete", "view"]

# 60 minutes x 60 seconds
CACHE_BY_HOUR = 60 * 60
CACHE_BY_DAY = 24 * CACHE_BY_HOUR


class ModelField:
    CharField = 'CharField'
    IntegerField = 'IntegerField'
    DecimalField = 'DecimalField'
    EmailField = 'EmailField'
    BooleanField = 'BooleanField'
    DateField = 'DateField'
    TimeField = 'TimeField'
    DateTimeField = 'DateTimeField'
    JSONField = 'JSONField'
    HTMLField = 'HTMLField'
    BigAutoField = 'BigAutoField'
    PositiveIntegerField = 'PositiveIntegerField'
    PositiveSmallIntegerField = 'PositiveSmallIntegerField'
    ManyToManyField = 'ManyToManyField'
    ImageField = 'ImageField'
    FileField = 'FileField'
    OneToOneField = 'OneToOneField'
    TextField = 'TextField'
    ForeignKey = 'ForeignKey'