from django.contrib import admin

from django_admin.admin import BaseModelAdmin

from .models import ModelDocumentation


class AdminModelDocumentationAdmin(BaseModelAdmin):
    list_display = ['app_model_name']
    list_display_links = ['app_model_name']

admin.site.register(ModelDocumentation, AdminModelDocumentationAdmin)
