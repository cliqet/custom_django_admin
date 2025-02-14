import json
import logging
import re
from typing import Any

from django.contrib import admin
from django.contrib.admin import site
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import Model, Q, QuerySet
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from django_admin.decorators import has_model_permission
from django_admin.permissions import IsSuperUser, has_user_permission
from services.cloudflare import verify_token
from services.queue_service import (
    delete_jobs,
    get_failed_jobs,
    get_job,
    get_queue_list,
    requeue_jobs,
)

from .actions import ACTIONS
from .configuration import APP_LIST_CONFIG_OVERRIDE
from .constants import DASHBOARD_URL_PREFIX
from .data_transform import transform_dict_to_camel_case
from .docs import (
    ADD_CHANGE_MODEL_RECORD_ERROR_DOC,
    ADD_MODEL_RECORD_DOC,
    CHANGE_MODEL_RECORD_DOC,
    CUSTOM_ACTION_VIEW_DOC,
    DELETE_MODEL_RECORD_DOC,
    DELETE_MODEL_RECORD_ERROR_DOC,
    GET_APPS_DOC,
    GET_CONTENT_TYPES_DOC,
    GET_FAILED_QUEUED_JOBS_DOC,
    GET_GROUPS_DOC,
    GET_LOG_ENTRIES_DOC,
    GET_MODEL_ADMIN_SETTINGS_DOC,
    GET_MODEL_FIELDS_DOC,
    GET_MODEL_LISTVIEW_DOC,
    GET_MODEL_RECORD_DOC,
    GET_PERMISSIONS_DOC,
    GET_QUEUED_JOB_DOC,
    GET_WORKER_QUEUES_DOC,
    QUERY_BUILDER_DOC,
    QUERY_BUILDER_ERROR_DOC,
    REQUEUE_FAILED_JOB_DOC,
    VERIFY_CLOUDFLARE_TOKEN_DOC,
    VERIFY_CLOUDFLARE_TOKEN_ERROR_DOC,
)
from .serializers import (
    AppSerializer,
    ContentTypeSerializer,
    GroupSerializer,
    LogEntrySerializer,
    ModelAdminSettingsSerializer,
    ModelFieldSerializer,
    PermissionSerializer,
    QueryBuilderBodySerializer,
    QueuedJobSerializer,
    RawQueryBodySerializer,
    RequeueOrDeleteJobsBodySerializer,
    VerifyTokenBodySerializer,
)
from .util_models import (
    get_converted_pk,
    get_model,
    get_model_fields_data,
    is_valid_modelfield_file,
)
from .util_serializers import (
    create_post_body_model_serializer,
    get_dynamic_serializer,
)
from .utils import (
    build_conditions_query,
    serialize_model_admin,
    transform_conditions_query,
)

log = logging.getLogger(__name__)


@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=AppSerializer,
            description=GET_APPS_DOC
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_apps(request):
    app_list = site.get_app_list(request)

    # Replace /admin with custom admin url prefix
    for app in app_list:
        app['app_url'] = f'{DASHBOARD_URL_PREFIX}{app.get('app_url')[6:-1]}'

        app_override = APP_LIST_CONFIG_OVERRIDE.get(app.get('app_label'))

        # Check if app has override
        if app_override:
            app['app_url'] = app_override.get('app_url')

        for model in app.get('models'):
            # Check if model in app has override
            if app_override:
                model_override = app_override.get('models', {}).get(model.get('object_name'))
            else:
                model_override = None
            
            if model.get('admin_url'):
                model['admin_url'] = f'{DASHBOARD_URL_PREFIX}{model.get('admin_url')[6:-1]}'

            # If app.model has override
            if app_override and model_override:
                model['admin_url'] = model_override.get('admin_url')

            if model.get('add_url'):
                model['add_url'] = f'{DASHBOARD_URL_PREFIX}{model.get('add_url')[6:-1]}'

            # If app.model has override
            if app_override and model_override:
                model['add_url'] = model_override.get('add_url')
    return Response(transform_dict_to_camel_case({
        'app_list': AppSerializer(app_list, many=True).data
    }), status=status.HTTP_200_OK)


@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=ModelFieldSerializer,
            description=GET_MODEL_FIELDS_DOC
        ),
        status.HTTP_404_NOT_FOUND: OpenApiResponse(
            description='Model fields not found. Returns []'
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_model_fields(request, app_label: str, model_name: str):
    try:
        model = get_model(f'{app_label}.{model_name}')

        has_permission, response = has_user_permission(request, model, 'view')
        if not has_permission:
            return response

        return Response({
            'fields': get_model_fields_data(model),
        }, status=status.HTTP_200_OK)
    except LookupError as e:
        log.error(f'Nothing found for app:{app_label} and model:{model_name} - {e}')

        return Response({
            'fields': [],
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        log.error(f'An error of type {type(e).__name__} occurred: {e}')

        return Response({
            'fields': [],
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=ModelAdminSettingsSerializer,
            description=GET_MODEL_ADMIN_SETTINGS_DOC
        ),
        status.HTTP_404_NOT_FOUND: OpenApiResponse(
            description='Model admin settings not found. Returns {}'
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_model_admin_settings(request, app_label: str, model_name: str):
    try:
        model = get_model(f'{app_label}.{model_name}')
        model_admin = admin.site._registry.get(model)
        model_admin_settings = serialize_model_admin(app_label, model, model_admin)

        return Response({
            'model_admin_settings': model_admin_settings
        }, status=status.HTTP_200_OK)
    except LookupError as e:
        log.error(f'Nothing found for app:{app_label} and model:{model_name} - {e}')

        return Response({
            'model_admin_settings': {}
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        log.error(f'An error of type {type(e).__name__} occurred: {e}')

        return Response({
            'model_admin_settings': {}
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=ModelFieldSerializer,
            description=GET_MODEL_FIELDS_DOC
        ),
        status.HTTP_404_NOT_FOUND: OpenApiResponse(
            description='Model fields not found. Returns []'
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_model_fields_edit(request, app_label: str, model_name: str, pk: str):
    try:
        model = get_model(f'{app_label}.{model_name}')

        has_permission, response = has_user_permission(request, model, 'edit')
        if not has_permission:
            return response

        model_admin = admin.site._registry.get(model)
        model_admin_settings = serialize_model_admin(app_label, model, model_admin)
        instance = model.objects.get(pk=pk)
        model_fields = get_model_fields_data(model, is_edit=True, instance=instance)

        return Response({
            'fields': model_fields,
            'model_admin_settings': model_admin_settings
        }, status=status.HTTP_200_OK)
    except model.DoesNotExist as e:
        log.error(f'Nothing found for app:{app_label} and model:{model_name} - {e}')

        return Response({
            'fields': [],
            'model_admin_settings': {}
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        log.error(f'An error of type {type(e).__name__} occurred: {e}')
        return Response({
            'fields': [],
            'model_admin_settings': {}
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=PermissionSerializer,
            description=GET_PERMISSIONS_DOC
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_permissions(request):
    permissions = Permission.objects.all()

    return Response(transform_dict_to_camel_case({
        'permissions': PermissionSerializer(permissions, many=True).data
    }), status=status.HTTP_200_OK)


@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=ContentTypeSerializer,
            description=GET_CONTENT_TYPES_DOC
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_content_types(request):
    content_types = ContentType.objects.all()

    return Response(transform_dict_to_camel_case({
        'content_types': ContentTypeSerializer(content_types, many=True).data
    }), status=status.HTTP_200_OK)


@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=GroupSerializer,
            description=GET_GROUPS_DOC
        ),
    }
)
@api_view(['GET'])
@has_model_permission(Group, 'view')
@permission_classes([IsAdminUser])
def get_groups(request):
    groups = Group.objects.all()

    return Response(transform_dict_to_camel_case({
        'groups': GroupSerializer(groups, many=True).data
    }), status=status.HTTP_200_OK)


@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=LogEntrySerializer,
            description=GET_LOG_ENTRIES_DOC
        ),
    }
)
@api_view(['GET'])
@has_model_permission(LogEntry, 'view')
@permission_classes([IsAdminUser])
def get_log_entries(request):
    log_entries = LogEntry.objects.all()

    return Response(transform_dict_to_camel_case({
        'log_entries': LogEntrySerializer(log_entries, many=True).data
    }), status=status.HTTP_200_OK)


@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            description=GET_MODEL_RECORD_DOC
        ),
        status.HTTP_404_NOT_FOUND: OpenApiResponse(
            description='Model record not found. Returns None'
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_model_record(request, app_label: str, model_name: str, pk: str):
    try:
        model = get_model(f'{app_label}.{model_name}')

        has_permission, response = has_user_permission(request, model, 'view')
        if not has_permission:
            return response

        record = model.objects.get(pk=pk)
        serializer_class = get_dynamic_serializer(app_label, model)
        serialized_record = serializer_class(record).data
        serialized_record['pk'] = pk

        return Response({
            'record': serialized_record
        }, status=status.HTTP_200_OK)
    except Exception:
        return Response({
            'record': None
        }, status=status.HTTP_404_NOT_FOUND)
    

@extend_schema(
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            description=CHANGE_MODEL_RECORD_DOC
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            description=ADD_CHANGE_MODEL_RECORD_ERROR_DOC
        ),
    }
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def change_model_record(request, app_label: str, model_name: str, pk: str):
    boolean_values = {
        'true': True,
        'false': False,
    }

    try:
        model = get_model(f'{app_label}.{model_name}')

        has_permission, response = has_user_permission(request, model, 'edit')
        if not has_permission:
            return response

        instance = model.objects.get(pk=pk)
        model_fields_data = get_model_fields_data(model)

        # validate post body
        body = request.data
        serializer = create_post_body_model_serializer(model_fields_data, is_editing=True)
        post_body_serializer: Serializer = serializer(data=body)

        error_messages = {}

        if post_body_serializer.is_valid():
            instance_data = {}
            for key, value in body.items():
                if model_fields_data.get(key).get('type') == 'ManyToManyField':
                    if value:
                        instance_data[key] = value.split(',')
                elif model_fields_data.get(key).get('type') == 'BooleanField':
                    instance_data[key] = boolean_values[value]
                elif model_fields_data.get(key).get('type') in ['FileField', 'ImageField']:
                    # If no file was passed, it must not be required
                    if value == '':
                        continue
                    else:
                        valid_file_data = is_valid_modelfield_file(
                            model_fields_data.get(key).get('help_text'),
                            request.FILES[key]
                        )
                        
                        if valid_file_data.get('is_valid_type') and valid_file_data.get('is_valid_size'):
                            instance_data[key] = request.FILES[key]
                        else:
                            error_messages[key] = []
                            if not valid_file_data.get('is_valid_type'):
                                error_msg = 'Invalid file type'
                                error_messages[key].append(error_msg)
                            if not valid_file_data.get('is_valid_size'):
                                error_msg = 'Invalid file size'
                                error_messages[key].append(error_msg)
                            raise ValidationError(error_msg)
                elif key == 'password':
                    # password was not updated
                    if value == '':
                        continue
                    else:
                        validate_password(value)
                else:
                    instance_data[key] = value

            # Update the instance with new data
            for key, value in instance_data.items():
                related_pk = get_converted_pk(value)

                if hasattr(instance, key):
                    field_type = model_fields_data.get(key).get('type')
                    
                    if field_type == 'ManyToManyField':
                        # Update ManyToManyField relationships
                        getattr(instance, key).set(related_pk)  # Use getattr to call set() dynamically
                        
                    elif field_type in ['ForeignKey', 'OneToOneField']:
                        # Retrieve the related instance using the provided pk
                        related_model = model._meta.get_field(key).related_model
                        instance_type = related_model.objects.get(pk=related_pk)  # Ensure value is the correct pk
                        setattr(instance, key, instance_type)  # Assign the related instance
                        
                    else:
                        # Handle other field types
                        setattr(instance, key, value)

            instance.save()
            instance.refresh_from_db()

            return Response({
                'message': f'Updated record [{instance.__str__()}] with pk {instance.pk} successfully'
            }, status=status.HTTP_201_CREATED)
        
        # Serialization errors
        for field, errors in post_body_serializer.errors.items():
            error_messages[field] = [str(error) for error in errors]

        log.error(f'Serialization error: {error_messages}')

        return Response({
            'message': 'Invalid data',
            'validation_error': error_messages
        }, status=status.HTTP_400_BAD_REQUEST)
    # Custom validation errors used for files
    except ValidationError as e:
        log.error(f'Validation error: {str(e)}')

        return Response({
            'message': 'Invalid data',
            'validation_error': error_messages
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        log.error(f'Error: {str(e)}')

        return Response({
            'message': str(e),
            'has_error': True
        }, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    responses={
        status.HTTP_202_ACCEPTED: OpenApiResponse(
            description=DELETE_MODEL_RECORD_DOC
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            description=DELETE_MODEL_RECORD_ERROR_DOC
        ),
    }
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_model_record(request, app_label: str, model_name: str, pk: str):
    try:
        model = get_model(f'{app_label}.{model_name}')

        has_permission, response = has_user_permission(request, model, 'delete')
        if not has_permission:
            return response

        instance = model.objects.get(pk=pk)
        instance.delete()

        return Response({
            'message': f'Deleted record [{instance.__str__()}] with pk {pk} successfully'
        }, status=status.HTTP_202_ACCEPTED)
    except Exception as e:
        log.error(f'Error: {str(e)}')

        return Response({
            'message': str(e),
            'has_error': True
        }, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            description=ADD_MODEL_RECORD_DOC
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            description=ADD_CHANGE_MODEL_RECORD_ERROR_DOC
        ),
    }
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_model_record(request, app_label: str, model_name: str):
    boolean_values = {
        'true': True,
        'false': False,
    }

    try:
        model = get_model(f'{app_label}.{model_name}')

        has_permission, response = has_user_permission(request, model, 'add')
        if not has_permission:
            return response

        model_fields_data = get_model_fields_data(model)

        # validate post body
        body = request.data

        serializer = create_post_body_model_serializer(model_fields_data, is_editing=True)
        post_body_serializer: Serializer = serializer(data=body)

        error_messages = {}

        if post_body_serializer.is_valid():
            instance_data = {}
            many_to_many_data = {}  # To hold ManyToManyField data
            foreignkey_data = {} # To hold ForeignKey data

            for key, value in body.items():
                # store many to many field list first if there is data and not an empty string
                if model_fields_data.get(key).get('type') == 'ManyToManyField':
                    if value:
                        many_to_many_data[key] = value.split(',')
                elif model_fields_data.get(key).get('type') in ['ForeignKey', 'OneToOneField']:
                    foreignkey_data[key] = value
                elif model_fields_data.get(key).get('type') == 'BooleanField':
                    instance_data[key] = boolean_values[value]
                elif model_fields_data.get(key).get('type') in ['FileField', 'ImageField']:
                    # If no file was passed, it must not be required
                    if value == '':
                        continue
                    else:
                        valid_file_data = is_valid_modelfield_file(
                            model_fields_data.get(key).get('help_text'),
                            request.FILES[key]
                        )

                        if valid_file_data.get('is_valid_type') and valid_file_data.get('is_valid_size'):
                            instance_data[key] = request.FILES[key]
                        else:
                            error_messages[key] = []
                            if not valid_file_data.get('is_valid_type'):
                                error_msg = 'Invalid file type'
                                error_messages[key].append(error_msg)
                            if not valid_file_data.get('is_valid_size'):
                                error_msg = 'Invalid file size'
                                error_messages[key].append(error_msg)
                            raise ValidationError(error_msg)
                else:
                    instance_data[key] = value

            # Handle foreign key field
            for key, value in foreignkey_data.items():
                # Retrieve the related model
                related_model = model._meta.get_field(key).related_model
                
                if value:  # Check if value is provided
                    related_pk = get_converted_pk(value)

                    try:
                        related_object = related_model.objects.get(pk=related_pk)  # Ensure value is the correct pk
                        instance_data[key] = related_object
                    except related_model.DoesNotExist:
                        error_msg = f'Related object with PK {related_pk} does not exist.'
                        error_messages[key].append(error_msg)
                        raise ValidationError(error_msg)
                else:
                    instance_data[key] = None

            # Ensure uid is not included
            if instance_data.get('uid') is not None:
                del instance_data['uid']

            # Ensure password is set
            password = instance_data.pop('password', None)

            # Create a new instance
            instance: Model = model(**instance_data)
            if password:
                instance.set_password(password)
            instance.save()

            # Handle many to many field
            for key, value in many_to_many_data.items():
                if hasattr(instance, key):
                    related_objects = []

                    # Get related objects for each pk
                    for related_pk in value:
                        # Convert pk to an int if pk is a number
                        # If it fails, then it must be a uid or a string type of pk
                        try:
                            converted_related_pk = int(related_pk)
                        except Exception:
                            converted_related_pk = related_pk
                        
                        try:
                            related_instance = model._meta.get_field(key).related_model.objects.get(pk=converted_related_pk)
                            related_objects.append(related_instance)
                        except model._meta.get_field(key).related_model.DoesNotExist:
                            error_msg = f'Related object with PK {related_pk} does not exist.'
                            error_messages[key].append(error_msg)
                            raise ValidationError(error_msg)

                    # Set the ManyToManyField relationships
                    getattr(instance, key).set(related_objects)

            instance.save()
            instance.refresh_from_db()

            return Response({
                'message': f'Created record [{instance.__str__()}] with pk {instance.pk} successfully'
            }, status=status.HTTP_201_CREATED)
        
        # If there are serialization errors
        for field, errors in post_body_serializer.errors.items():
            error_messages[field] = [str(error) for error in errors]

        log.error(f'Serialization error: {error_messages}')
        
        return Response({
            'message': 'Invalid data',
            'validation_error': error_messages
        }, status=status.HTTP_400_BAD_REQUEST)
    # Custom validation errors used for files
    except ValidationError as e:
        log.error(f'Validation error: {str(e)}')

        return Response({
            'message': 'Invalid data',
            'validation_error': error_messages
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        log.error(f'Error: {str(e)}')

        return Response({
            'message': str(e),
            'has_error': True
        }, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            description=GET_MODEL_LISTVIEW_DOC
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            description='Error on request'
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_model_listview(request, app_label: str, model_name: str):
    try:
        model = get_model(f'{app_label}.{model_name}')

        has_permission, response = has_user_permission(request, model, 'view')
        if not has_permission:
            return response

        serializer = get_dynamic_serializer(app_label, model)
        model_admin = admin.site._registry.get(model)
        search_fields = model_admin.search_fields

        # Retrieve query parameters for filtering
        filter_params = {
            f'{key}__in': json.loads(value)
            for key, value in request.GET.items() 
            if key not in ['limit', 'offset', 'custom_search']
        }
        search_value = request.GET.get('custom_search')

        # Query the model
        # No filters and search
        if not filter_params and not search_value:
            queryset = model.objects.all()

        # No filters but with search
        if not filter_params and search_value:
            search_query = Q()
            for field in search_fields:
                search_query |= Q(**{f'{field}__icontains': search_value})
            queryset = model.objects.filter(search_query)

        # With filters and search
        if filter_params and search_value:
            search_query = Q()
            for field in search_fields:
                search_query |= Q(**{f'{field}__icontains': search_value})
            queryset = model.objects.filter(**filter_params).filter(search_query)

        # With filters and no search    
        if filter_params and not search_value:
            queryset = model.objects.filter(**filter_params)

        # If there is modeladmin ordering
        for ordering in model_admin.ordering:
            queryset = queryset.order_by(ordering)

        # Initialize pagination
        paginator = LimitOffsetPagination()

        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Serialize the paginated data
        serialized_data = serializer(paginated_queryset, many=True)

        paginated_data = paginator.get_paginated_response(serialized_data.data)
    
        return Response(
            paginated_data.data,
            status=status.HTTP_200_OK
        )
    except Exception as e:
        log.error(f'Error getting paginated model listview: {e}')
        return Response(
            None,
            status=status.HTTP_400_BAD_REQUEST
        )
    

@extend_schema(
    responses={
        status.HTTP_202_ACCEPTED: OpenApiResponse(
            description=CUSTOM_ACTION_VIEW_DOC
        ),
        status.HTTP_422_UNPROCESSABLE_ENTITY: OpenApiResponse(
            description='Error in request'
        ),
    }
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def custom_action_view(request, app_label: str, model_name: str, func: str):
    try:
        body = request.data
        pk_list = body.get('payload')
        if not isinstance(pk_list, list):
            return Response({
                'message': 'Invalid payload'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Call custom action based on func name
        action_response = ACTIONS[func](request, app_label, model_name, pk_list)

        return action_response
    except Exception as e:
        log.error(f'Error in custom action view: {e}')
        return Response(
            None,
            status=status.HTTP_400_BAD_REQUEST
        )
    
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_inline_listview(request, parent_app_label: str, parent_model_name: str):
    try:
        model = get_model(f'{parent_app_label}.{parent_model_name}')

        has_permission, response = has_user_permission(request, model, 'view')
        if not has_permission:
            return response
        
        model_admin = admin.site._registry.get(model)
        custom_inlines = model_admin.custom_inlines
        inline_class_query = request.GET.get('inline_class')
        inline_class = None

        # Get the inline class
        for inline in custom_inlines:
            if inline.__name__ == inline_class_query:
                inline_class = inline()
                break

        queryset = inline_class.get_queryset()

        inline_model = get_model(f'{inline_class.app_label}.{inline_class.model_name}')
        has_permission, response = has_user_permission(request, model, 'view')
        if not has_permission:
            return response

        serializer = get_dynamic_serializer(inline_class.app_label, inline_model)

        # Initialize pagination
        paginator = LimitOffsetPagination()

        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Serialize the paginated data
        serialized_data = serializer(paginated_queryset, many=True)

        paginated_data = paginator.get_paginated_response(serialized_data.data)

        return Response(
            paginated_data.data,
            status=status.HTTP_200_OK
        )
    except Exception as e:
        log.error(f'Error getting paginated inline listview: {e}')
        return Response(
            None,
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    request=VerifyTokenBodySerializer,
    responses={
        status.HTTP_202_ACCEPTED: OpenApiResponse(
            description=VERIFY_CLOUDFLARE_TOKEN_DOC
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            description=VERIFY_CLOUDFLARE_TOKEN_ERROR_DOC
        ),
    }
)
@api_view(['POST'])
def verify_cloudflare_token(request):
    try:
        body = request.data
        serialized_body = VerifyTokenBodySerializer(data=body)

        if serialized_body.is_valid():
            token = body.get('token')
            is_valid = verify_token(request, token)

            return Response(transform_dict_to_camel_case({
                'is_valid': is_valid
            }), status=status.HTTP_202_ACCEPTED)
    except Exception as e:
        log.error(f'Error verifying cloudflare turnstile token: {str(e)}')

        return Response(transform_dict_to_camel_case({
            'is_valid': False
        }), status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            description=GET_WORKER_QUEUES_DOC
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser, IsSuperUser])
def get_worker_queues(request):
    try:
        queues = get_queue_list()

        return Response({
            'queues': queues
        }, status=status.HTTP_200_OK)
    except Exception as e:
        log.error(f'Error retrieving worker queues: {str(e)}')

        return Response({
            'queues': []
        }, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            description=GET_FAILED_QUEUED_JOBS_DOC
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser, IsSuperUser])
def get_failed_queued_jobs(request, queue_name: str):
    try:
        jobs = get_failed_jobs(queue_name)
        serialized_jobs = QueuedJobSerializer(jobs, many=True).data

        return Response({
            'failed_jobs': {
                'results': serialized_jobs,
                'count': len(jobs),
                'table_fields': ['id', 'created_at', 'enqueued_at', 'ended_at', 'callable']
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        log.error(f'Error retrieving queue failed jobs for {queue_name}: {str(e)}')

        return Response({
            'failed_jobs': {
                'results': [],
                'count': 0,
                'table_fields': ['id', 'created_at', 'enqueued_at', 'ended_at', 'callable']
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            description=GET_QUEUED_JOB_DOC
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser, IsSuperUser])
def get_queued_job(request, queue_name: str, job_id: str):
    try:
        job = get_job(queue_name, job_id)

        return Response({
            'job': QueuedJobSerializer(job).data,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        log.error(f'Error retrieving job id {job_id} from queue {queue_name}: {str(e)}')

        return Response({
            'job': None,
        }, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(
    request=RequeueOrDeleteJobsBodySerializer,
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            description=REQUEUE_FAILED_JOB_DOC
        ),
    }
)
@api_view(['POST'])
@permission_classes([IsAdminUser, IsSuperUser])
def requeue_failed_jobs(request):
    try:
        body = request.data
        data = RequeueOrDeleteJobsBodySerializer(data=body)
        if not data.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request'
            }, status=status.HTTP_400_BAD_REQUEST)

        requeue_jobs(body.get('queue_name'), body.get('job_ids'))

        jobs_ids_str = '<ul class="list-disc">'
        for job_id in body.get('job_ids'):
            jobs_ids_str += f'<li>{job_id}</li>'
        jobs_ids_str += '</ul>'

        return Response({
            'success': True,
            'message': f"""
                <p>Successfully requeued jobs for queue {body.get('queue_name')}:</p>
                {jobs_ids_str}
            """

        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        log.error(f'Error requeueing jobs for {body}: {str(e)}')

        return Response({
            'success': False,
            'message': f'Something went wrong with your request'
        }, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    request=RequeueOrDeleteJobsBodySerializer,
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            description=GET_QUEUED_JOB_DOC
        ),
    }
)
@api_view(['POST'])
@permission_classes([IsAdminUser, IsSuperUser])
def delete_queued_jobs(request):
    try:
        body = request.data
        data = RequeueOrDeleteJobsBodySerializer(data=body)
        if not data.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request'
            }, status=status.HTTP_400_BAD_REQUEST)

        delete_jobs(body.get('queue_name'), body.get('job_ids'))

        jobs_ids_str = '<ul class="list-disc">'
        for job_id in body.get('job_ids'):
            jobs_ids_str += f'<li>{job_id}</li>'
        jobs_ids_str += '</ul>'

        return Response({
            'success': True,
            'message': f"""
                <p>Successfully deleted jobs for queue {body.get('queue_name')}:</p>
                {jobs_ids_str}
            """

        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        log.error(f'Error deleting jobs for {body}: {str(e)}')

        return Response({
            'success': False,
            'message': f'Something went wrong with your request'
        }, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    request=QueryBuilderBodySerializer,
    responses={
        status.HTTP_202_ACCEPTED: OpenApiResponse(
            description=QUERY_BUILDER_DOC
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            description=QUERY_BUILDER_ERROR_DOC
        ),
    }
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def query_builder(request):
    try:
        body = request.data
        serialized_body = QueryBuilderBodySerializer(data=body)

        if serialized_body.is_valid():
            app_name: str = body.get('app_name')
            model_name: str = body.get('model_name')

            model = get_model(f'{app_name}.{model_name.lower()}')
            model_fields_data = get_model_fields_data(model)

            conditions: list[list[str | Any]] = body.get('conditions')
            if conditions:
                model_fields_data = get_model_fields_data(model)
                transformed_conditions = transform_conditions_query(conditions, model_fields_data)

                query = build_conditions_query(transformed_conditions)
                results: QuerySet = model.objects.filter(query)
            else:
                results = model.objects.all()

            orderings: list[str] = body.get('orderings')
            for order in orderings:
                results = results.order_by(order)

            query_limit = body.get('query_limit')
            if query_limit:
                results = results[:query_limit]

            model_serializer = get_dynamic_serializer(app_name, model)
            serialized_results = model_serializer(results, many=True).data

            return Response({
                'count': len(results),
                'fields': list(model_fields_data.keys()),
                'results': serialized_results
            }, status=status.HTTP_202_ACCEPTED)
        
        # If there are serialization errors
        error_messages = {}
        for field, errors in serialized_body.errors.items():
            error_messages[field] = [str(error) for error in errors]
        
        return Response({
            'count': 0,
            'fields': [],
            'results': [],
            'message': 'Invalid data',
            'validation_error': error_messages
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        log.error(f'Error with query builder: {str(e)}')

        return Response({
            'count': 0,
            'fields': [],
            'results': [],
            'message': f'Error with query builder: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    request=RawQueryBodySerializer,
    responses={
        status.HTTP_202_ACCEPTED: OpenApiResponse(
            description=QUERY_BUILDER_DOC
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            description=QUERY_BUILDER_ERROR_DOC
        ),
    }
)
@api_view(['POST'])
@permission_classes([IsAdminUser, IsSuperUser])
def raw_query(request):
    try:
        body = request.data
        serialized_body = RawQueryBodySerializer(data=body)

        if serialized_body.is_valid():
            query = body.get('query')

            # NOTE: Remove this check if you want no limitations to the query
            # =============================================================
            query_lower = query.lower().strip()
            if re.search(r'\b(update|delete|drop|truncate|insert)\b', query_lower):
                return Response({
                    'count': 0,
                    'fields': [],
                    'results': [],
                    'message': 'Query is not allowed'
                }, status=status.HTTP_400_BAD_REQUEST)
            # =============================================================

            with connection.cursor() as cursor:
                cursor.execute(query)  
                columns = [col[0] for col in cursor.description]
                
                results = cursor.fetchall()  

                # Format results as a list of dictionaries
                response_data = [
                    dict(zip(columns, row)) for row in results
                ]

            return Response({
                'count': len(results),
                'fields': columns,
                'results': response_data,
            }, status=status.HTTP_202_ACCEPTED)
        
        # If there are serialization errors
        error_messages = {}
        for field, errors in serialized_body.errors.items():
            error_messages[field] = [str(error) for error in errors]
        
        return Response({
            'count': 0,
            'fields': [],
            'results': [],
            'message': 'Invalid data',
            'validation_error': error_messages
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        log.error(f'Error with query builder: {str(e)}')

        return Response({
            'count': 0,
            'fields': [],
            'results': [],
            'message': f'Error with query builder: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)