from typing import Tuple

from django.db.models import Model
from django.http import HttpRequest
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from backend.settings.base import APP_MODE, CORS_ALLOWED_ORIGINS, DjangoSettings

from .constants import PermissionType


class IsFromUiRequest(BasePermission):
    """
    Allows apis to be accessible only from the frontend.
    """
    def has_permission(self, request, view):
        if APP_MODE in [DjangoSettings.LOCAL, DjangoSettings.TEST]:
            return True
        
        origin = request.META.get('HTTP_ORIGIN')
    
        # Put additional conditions here
        conditions = [
            origin in CORS_ALLOWED_ORIGINS,
        ]

        if all(conditions):
            return True
        
        raise PermissionDenied('Forbidden request')
    

class IsSuperUser(BasePermission):
    """
        Custom permission class that grants access only to superusers.
    """

    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_staff and 
            request.user.is_active and 
            request.user.is_superuser
        )


def has_user_permission(
        request: HttpRequest, 
        model: Model, 
        permission: PermissionType) -> Tuple[bool, Response | None]:
    """
        Checks if a user has permission to perform the action on a model
    """
    perm = f"{model._meta.app_label}.{permission}_{model._meta.model_name}"
            
    # Check if the user has the required permission
    if not request.user.has_perm(perm):
        return False, Response({
            'detail': 'You do not have permission to perform this action.'
        }, status=status.HTTP_403_FORBIDDEN)

    return True, None




        