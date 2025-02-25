from django.contrib import admin

from django_admin.admin import BaseModelAdmin

from .models import SavedQueryBuilder, SavedRawQuery


class SavedQueryBuilderAdmin(BaseModelAdmin):
    list_display = ['name']


class SavedRawQueryAdmin(BaseModelAdmin):
    list_display = ['name']


admin.site.register(SavedQueryBuilder, SavedQueryBuilderAdmin)
admin.site.register(SavedRawQuery, SavedRawQueryAdmin)