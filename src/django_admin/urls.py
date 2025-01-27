from django.urls import path

from .views import (
    add_model_record,
    change_model_record,
    custom_action_view,
    get_apps,
    get_content_types,
    get_groups,
    get_inline_listview,
    get_log_entries,
    get_model_admin_settings,
    get_model_fields,
    get_model_fields_edit,
    get_model_listview,
    get_model_record,
    get_permissions,
    verify_cloudflare_token,
)

urlpatterns = [
    path('apps', get_apps, name='get_apps'),
    path('permissions', get_permissions, name='get_permissions'),
    path('log-entries', get_log_entries, name='get_log_entries'),
    path('content-types', get_content_types, name='get_content_types'),
    path('groups', get_groups, name='get_groups'),
    path('model-listview-action/<str:app_label>/<str:model_name>/<str:func>', custom_action_view, name='custom_action_view'),
    path('model-listview/<str:app_label>/<str:model_name>', get_model_listview, name='get_model_listview'),
    path('inline-listview/<str:parent_app_label>/<str:parent_model_name>', get_inline_listview, name='get_inline_listview'),
    path('add-record/<str:app_label>/<str:model_name>', add_model_record, name='add_model_record'),
    path('change-record/<str:app_label>/<str:model_name>/<str:pk>', change_model_record, name='change_model_record'),
    path('model/<str:app_label>/<str:model_name>/<str:pk>', get_model_record, name='get_model_record'),
    path('model-fields/<str:app_label>/<str:model_name>/<str:pk>', get_model_fields_edit, name='get_model_fields_edit'),
    path('model-fields/<str:app_label>/<str:model_name>', get_model_fields, name='get_model_fields'),
    path('model-admin-settings/<str:app_label>/<str:model_name>', get_model_admin_settings, name='get_model_admin_settings'),
    path('verify-cloudflare-token', verify_cloudflare_token, name='verify_cloudflare_token'),
]
