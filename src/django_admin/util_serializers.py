from importlib import import_module

from django.db.models import Model
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


def get_serializer(app_name: str, serializer_class_name: str) -> ModelSerializer:
    """ Look up a drf serializer model from an "<app_name>.serializers" path """
    module_path = f"{app_name}.serializers"
    module = import_module(module_path)
    serializer_class = getattr(module, serializer_class_name, None)

    return serializer_class


def get_dynamic_serializer(app_name: str, model: Model) -> ModelSerializer:
    """ 
        Look up a drf serializer model from an "<app_name>.serializers" path
        based on model.
    """

    # replaces 3rd party apps or django apps where apps are not defined in source code to django_admin
    # NOTE: You must have a serializer class defined in django_admin.serializers for these.
    third_party_apps = ['token_blacklist']

    django_builtin_apps = ['admin', 'auth']

    # These are serializers for models where models are not defined in the code
    outside_serializers = {
        'BlacklistedToken': 'BlacklistedTokenSerializer',
        'OutstandingToken': 'OutstandingTokenSerializer',
        'LogEntry': 'LogEntrySerializer',
        'Group': 'GroupSerializer',
    }

    # Handle 3rd party apps
    if app_name in third_party_apps or app_name in django_builtin_apps:
        app_name: str = 'django_admin'
        serializer_classname: str = outside_serializers.get(model.__name__)
    else:
        serializer_classname: str = model.serializer_classname
        

    module_path = f"{app_name}.serializers"
    module = import_module(module_path)
    serializer_class = getattr(module, serializer_classname, None)

    return serializer_class


def create_post_body_model_serializer(model_fields_data: dict, is_editing: bool = False) -> serializers.Serializer:
    """
        Creates a serializer used for validating a post request body when adding or changing 
        a model record. The serializer will have fields based on fields of the record
    """
    other_serializer_fields = {
        'EmailField': serializers.EmailField(),
        'TextField': serializers.CharField(),
        'BooleanField': serializers.BooleanField(),
        'DateField': serializers.DateField(),
        'TimeField': serializers.TimeField(),
        'DateTimeField': serializers.DateTimeField(),
        'JSONField': serializers.JSONField(),
        'HTMLField': serializers.CharField(),
    }

    serializer_fields = {}
    for field_name, data in model_fields_data.items():
        # skip fields that are not required
        # these are auto-generated fields
        if field_name in ['created_at', 'updated_at']:
            continue

        # these are auto-generated fields
        elif data.get('type') == 'BigAutoField' or field_name == 'uid':
            continue

        # fields that are not required
        elif not data.get('required'):
            continue

        elif field_name == 'password' and is_editing:
            continue

        elif data.get('type') == 'CharField':
            serializer_fields[field_name] = serializers.CharField(
                max_length=data.get('max_length'),
                min_length=1 if data.get('required') else None,
                required=data.get('required')
            )

        elif data.get('type') in ['IntegerField', 'PositiveIntegerField', 'PositiveSmallIntegerField']:
            serializer_fields[field_name] = serializers.IntegerField(
                max_value=data.get('max_value') or None,
                min_value=data.get('min_value') or None
            )

        elif data.get('type') == 'ManyToManyField':
            # May contain an empty string or comma separated pks. E.g. 1,2,5
            # It may be a pk as id or a uid
            serializer_fields[field_name] = serializers.CharField(
                required=data.get('required')
            )

        # When editing, do not require image and file fields since these should 
        # have been required when first created
        elif data.get('type') == 'ImageField' and is_editing:
            serializer_fields[field_name] = serializers.ImageField(required=False)

        elif data.get('type') == 'ImageField' and not is_editing:
            serializer_fields[field_name] = serializers.ImageField(required=True)

        elif data.get('type') == 'FileField' and is_editing:
            serializer_fields[field_name] = serializers.FileField(required=False)

        elif data.get('type') == 'FileField' and not is_editing:
            serializer_fields[field_name] = serializers.FileField(required=True)

        elif data.get('type') == 'DecimalField':
            serializer_fields[field_name] = serializers.DecimalField(
                max_digits=data.get('max_digits'),
                decimal_places=data.get('decimal_places')
            )

        # All other fields
        else:
            if other_serializer_fields.get(data.get('type')):
                serializer_fields[field_name] = other_serializer_fields.get(data.get('type'))

    DynamicSerializer = type('DynamicSerializer', (serializers.Serializer,), serializer_fields)
    return DynamicSerializer