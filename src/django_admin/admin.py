from enum import Enum

from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group
from django.db import models

# from django.contrib.sessions.models import Session
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from django_admin.util_models import get_model

from .constants import LIST_PAGE_COUNT

# Add serializer class property to builtin Django models and 3rd party apps
# Handled in common.util_serializers.get_dynamic_serializer
LogEntry.admin_serializer_classname = 'AdminLogEntrySerializer'
Group.admin_serializer_classname = 'AdminGroupSerializer'
BlacklistedToken.admin_serializer_classname = 'AdminBlacklistedTokenSerializer'
OutstandingToken.admin_serializer_classname = 'AdminOutstandingTokenSerializer'


class CUSTOM_ACTIONS(Enum):
    """
        Define all custom action names here
    """
    DELETE_LISTVIEW = 'delete'


class BaseModelAdmin(admin.ModelAdmin):
    """
        Use this for all ModelAdmin classes.
        These are the supported model admin properties
    """
    list_per_page = LIST_PAGE_COUNT
    list_filter = []
    list_display = []
    list_display_links = []
    search_fields = []
    search_help_text = ''
    ordering = []
    fieldsets = ()
    autocomplete_fields = []

    # Extend these
    readonly_fields = ['created_at', 'updated_at']
    custom_actions = [{
        'func': CUSTOM_ACTIONS.DELETE_LISTVIEW.value,
        'label': 'Delete selected records'
    }]
    custom_inlines = []

    # A prefix custom route to use for the change link. A /<pk>/change will 
    # be appended. Do not put a trailing slash
    # Handle the custom route in the frontend
    custom_change_link = ''

    # Use for any dynamic component you want to render after custom inlines
    # Put strings which you will use as identifiers for UI to check
    extra_inlines = []

    # Data is autopopulated when list_filter is not empty
    table_filters = []


class CustomTabularInlineBase(type):
    def __new__(cls, name, bases, attrs):
        return super().__new__(cls, name, bases, attrs)
    

class CustomTabularInline(metaclass=CustomTabularInlineBase):
    def __init__(self, *args, **kwargs):
        for field_name, value in kwargs.items():
            setattr(self, field_name, value)


class BaseCustomInline(CustomTabularInline):
    """
        Base class to use for all custom inlines
    """
    # The app the model belongs to (all lowercase)
    app_label = ''
    # The model name (all lowercase)
    model_name = ''
    # A label (for the UI) to use for the model name
    model_name_label = ''
    # The fields to be displayed in the table
    list_display = ['pk']
    # The field which should be a link to the change form of the record.
    # Field should be present in list_display
    list_display_links = ['pk']
    list_per_page = LIST_PAGE_COUNT

    # A prefix custom route to use for the change link. A /<pk>/change will 
    # be appended. Do not put a trailing slash
    # Handle the custom route in the frontend
    custom_change_link = ''

    # Override this if you want a custom queryset
    # change_obj is the current record being changed in the detail page
    def get_queryset(self, change_obj):
        custom_inline_model = get_model(f'{self.app_label}.{self.model_name}')

        queryset = custom_inline_model.objects.all()

        for field in custom_inline_model._meta.get_fields():
            if isinstance(field, models.ForeignKey) and field.related_model == change_obj.__class__:
                fk_field = field
                break

        if fk_field:
            # Filter the queryset based on the ForeignKey relationship
            queryset = queryset.filter(**{fk_field.name: change_obj})

        return queryset

    


# Builtin Django models =================================================
class GroupAdmin(BaseModelAdmin):
    fieldsets = (
        ('Group Settings', {
            'fields': ('name', 'permissions'),
        }),
    )
    filter_horizontal = ['permissions']
    readonly_fields = []


class LogEntryAdmin(BaseModelAdmin):
    """
        Log Properties
        'action_time', 'user', 'content_type', 'object_repr', 'change_message', 'action_flag'
    """
    list_display = ('id', 'action_time', 'user', 'content_type', 'action_flag')
    list_filter = ['action_flag', 'content_type']
    list_per_page = 20
    search_fields = ['content_type__model', 'content_type__app_label']
    readonly_fields = ('object_id', 'action_time', 'user', 'content_type',
                       'object_repr', 'change_message', 'action_flag')
    
    fieldsets = (
        ('Fields', {
            'fields': (
                'id', 'action_time', 'user', 'content_type', 'object_repr', 'change_message', 
                'action_flag'
            ),
        }),
    )


# You can only use this if your session uses db
# class SessionLogAdmin(admin.ModelAdmin):
#     list_display = ['session_key', 'expire_date']
#     list_per_page = 20
#     search_fields = ['session_key']
#     readonly_fields = ['session_key', 'session_data', 'expire_date']

#     fieldsets = (
#         ('Fields', {
#             'fields': ('session_key', 'session_data', 'expire_date'),
#         }),
#     )
# =================================================================


# 3rd party models =================================================
class BlacklistedTokenAdmin(BaseModelAdmin):
    fieldsets = (
        ('BlacklistedToken Settings', {
            'fields': ('id', 'token',),
        }),
    )
    readonly_fields = []


class OutstandingTokenAdmin(BaseModelAdmin):
    fieldsets = (
        ('OutstandingToken Settings', {
            'fields': ('jti', 'user'),
        }),
    )
    readonly_fields = []
# ===============================================================



admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
admin.site.unregister(BlacklistedToken)
admin.site.register(BlacklistedToken, BlacklistedTokenAdmin)
admin.site.unregister(OutstandingToken)
admin.site.register(OutstandingToken, OutstandingTokenAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
# admin.site.register(Session, SessionLogAdmin)


