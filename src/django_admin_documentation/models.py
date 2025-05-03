from django.contrib.admin import site
from django.db import models

from django_admin.models import BaseCachedModel, HTMLField


def get_app_model_choices():
    """
        Dynamically create choices based on current <app>.<models>
    """
    choices = [
        (f'{model._meta.app_label} - {model._meta.object_name.lower()}',
         f'{model._meta.app_label} - {model._meta.object_name.lower()}')
        for model, _ in site._registry.items()
    ]
    return sorted(choices, key=lambda x: x[0])

class ModelDocumentation(BaseCachedModel):
    """
        Add documentation for your models for the admin to view.
        Accessible via /<admin_dashboard_prefix>/model-docs
    """
    CACHE_KEY_PREFIX = 'ModelDocs'
    admin_serializer_classname = 'AdminModelDocumentationSerializer'

    app_model_name = models.CharField(
        max_length=50, 
        help_text='The app - model name', 
        choices=get_app_model_choices,
        unique=True
    )
    content = HTMLField(help_text='Enter content here')

    def __str__(self):
        return self.app_model_name
