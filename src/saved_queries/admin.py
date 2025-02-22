from django.contrib import admin

from django_admin.admin import BaseModelAdmin

from .models import SavedQueryBuilder


class SavedQueryBuilderAdmin(BaseModelAdmin):
    list_display = ['name']

admin.site.register(SavedQueryBuilder, SavedQueryBuilderAdmin)
