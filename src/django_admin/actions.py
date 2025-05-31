from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

from backend.settings.base import IS_DEMO_MODE
from django_admin.admin.admin_main import CUSTOM_ACTIONS
from django_admin.utils_models import get_model

from .permissions import has_user_permission
from .utils import copy_record

"""
DEFINE CUSTOM ACTIONS HERE.
Your custom actions should provide a custom response
"""


def delete_listview(request, app_label: str, model_name: str, pk_list: list[str]) -> dict:
    with transaction.atomic():
        model = get_model(f'{app_label}.{model_name}')

        has_permission, response = has_user_permission(request, model, 'delete')
        if not has_permission:
            return response

        records = model.objects.filter(pk__in=pk_list)
        records.delete()

        return Response({
            'message': f'Deleted {len(pk_list)} record/s successfully'
        },status=status.HTTP_202_ACCEPTED)


# Define custom action functions here for invocation
ACTIONS = {
    CUSTOM_ACTIONS.DELETE_LISTVIEW: delete_listview,
}

# For DEMO only and can be deleted
def copy_demo_model(request, app_label: str, model_name: str, pk_list: list[str]) -> dict:
    from uuid import uuid4

    with transaction.atomic():
        model = get_model(f'{app_label}.{model_name}')

        has_permission, response = has_user_permission(request, model, 'add')
        if not has_permission:
            return response

        records = model.objects.filter(pk__in=pk_list)
        error_messages = []
        for record in records:
            err_message = copy_record(
                record,
                {
                    # Because name field needs to be unique
                    'django_admin_demo.demomodel.name': lambda field_value: f'{field_value}-{uuid4()}',

                    # Example if you want copied records to be set to False for boolean field
                    'django_admin_demo.demomodel.is_active': lambda field_value: False,
                }
            )
            if err_message:
                error_messages.append(err_message)

        if not error_messages:
            return Response({
                'message': f'Copied {len(pk_list)} record/s successfully'
            },status=status.HTTP_202_ACCEPTED)
        else:
            flattened_errors = [str(item) for sublist in error_messages for item in sublist]
            html_error_message = '<ul>'
            for error in flattened_errors:
                html_error_message += f'<li>{error}</li>'
            html_error_message += '</ul>'

            return Response({
                'message': html_error_message
            },status=status.HTTP_422_UNPROCESSABLE_ENTITY)


if IS_DEMO_MODE:
    ACTIONS[CUSTOM_ACTIONS.COPY_DEMO_MODEL] = copy_demo_model
