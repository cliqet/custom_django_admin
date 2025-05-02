from django.db.models import ForeignKey, Model
from django.http.request import HttpRequest

from .admin import BaseModelAdmin
from .serializers import AdminCustomInlineSerializer


def get_model_perm(permission_code_name: str, model_name: str) -> str:
    return permission_code_name.replace(f'_{model_name}', '')


def serialize_model_admin(app_label: str, model: Model, model_admin: BaseModelAdmin) -> dict:
    """
        Serializes the model admin settings
    """
    if not model_admin:
        return None

    serialized_data = {
        'model_name': model.__name__,
        'app_label': app_label,
        'fieldsets': [],
        'list_display': model_admin.list_display,
        'list_per_page': model_admin.list_per_page,
        'list_display_links': model_admin.list_display_links,
        'search_fields': model_admin.search_fields,
        'search_help_text': model_admin.search_help_text,
        'list_filter': model_admin.list_filter,
        'readonly_fields': model_admin.readonly_fields,
        'ordering': model_admin.ordering,
        'custom_actions': model_admin.custom_actions,
        'autocomplete_fields': model_admin.autocomplete_fields,
        'table_filters': model_admin.table_filters,
        'custom_inlines': AdminCustomInlineSerializer(
            model_admin.custom_inlines,
            many=True
        ).data,
        'extra_inlines': model_admin.extra_inlines,
        'custom_change_link': model_admin.custom_change_link
    }

    pk_field = model._meta.pk.name

    # If there is no list display
    if not model_admin.list_display:
        serialized_data['list_display'] = [pk_field]

    # If list_display_links is not defined, make pk field name the default
    if not model_admin.list_display_links:
        # Just use the first in list display
        if pk_field not in serialized_data['list_display']:
            serialized_data['list_display_links'] = [serialized_data['list_display'][0]]
        else:
            serialized_data['list_display_links'] = [model._meta.pk.name]

    if not model_admin.search_fields:
        serialized_data['search_help_text'] = 'Search not available'

    if model_admin.list_filter:
        table_filters = []
        for field in model_admin.list_filter:
            table_filter_fields = {}
            table_filter_fields['field'] = field
            field_object = model._meta.get_field(field)
            initial_unique_field_values = [{'value': None, 'label': 'All'}]

            if isinstance(field_object, ForeignKey):
                related_model = field_object.related_model
                unique_related_instances = related_model.objects.distinct()
                unique_field_values = [
                    { 'value': instance.pk, 'label': str(instance)}
                    for instance in unique_related_instances
                ]
            elif field_object.choices:
                unique_field_values = [
                    {'value': val, 'label': label}
                    for val, label in field_object.choices
                ]
            else:
                unique_values = model.objects.values_list(field, flat=True).distinct()
                unique_field_values = [
                    {'value': val, 'label': str(val)}  
                    for val in unique_values
                ]
            table_filter_fields['values'] = initial_unique_field_values + unique_field_values
            table_filters.append(table_filter_fields)
        serialized_data['table_filters'] = table_filters

    # Organize and serialize fieldsets
    if model_admin.fieldsets:
        for title, options in model_admin.fieldsets:
            serialized_data['fieldsets'].append({
                'title': title,
                'fields': options['fields']
            })
    # If no fieldsets are defined in the model admin
    # Get all fields defined in the model
    else:
        serialized_data['fieldsets'].append({
            'title': 'Fields',
            'fields': [
                field.name for field in model._meta.get_fields()
                if (field.model == model and not field.auto_created) or field.name == 'id'
            ]
        })

    return serialized_data

def get_client_ip(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
