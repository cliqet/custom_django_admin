from functools import wraps

from django.db.models import Model
from rest_framework import status
from rest_framework.response import Response

from .constants import PermissionType


def has_model_permission(model: Model, permission: PermissionType):
    """
        Decorator to check model permissions of user
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Construct the permission string
            perm = f"{model._meta.app_label}.{permission}_{model._meta.model_name}"
            
            # Check if the user has the required permission
            if not request.user.has_perm(perm):
                return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
    