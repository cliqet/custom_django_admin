from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

from django_admin.admin import CUSTOM_ACTIONS
from django_admin.util_models import get_model

from .permissions import has_user_permission

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
    CUSTOM_ACTIONS.DELETE_LISTVIEW.value: delete_listview
}
