from django.contrib.auth.models import Permission

from django_admin.utils import get_model_perm

from .models import CustomUser


def organize_permissions(permissions: list, user: CustomUser) -> dict:
    obj = {}
    for permission in permissions:
        permission_id = permission.get('id')
        app_label = permission.get('content_type').get('app_label')
        model = permission.get('content_type').get('model')
        content_type_id = permission.get('content_type').get('id')
        permission_code_name = permission.get('codename')
        perm = get_model_perm(permission_code_name, model)

        # Handle special app / model cases
        # Admin log entries, allow only view permission
        if app_label == 'admin' and model == 'logentry' and not user.is_superuser:
            if perm == 'view':
                obj[app_label] = {}
                obj[app_label][model] = {
                    'id': content_type_id,
                    'perms_ids': {},
                    'perms': {}
                }
                obj[app_label][model]['perms'][perm] = permission_id
                obj[app_label][model]['perms_ids'][permission_id] = perm
            continue

        # Do not include content type
        if app_label == 'contenttypes':
            continue

        # Only view and delete for sessions app
        if app_label == 'sessions' and model == 'session':
            if perm == 'view' or perm == 'delete':
                if obj.get(app_label) is None:
                    obj[app_label] = {}
                    obj[app_label][model] = {
                        'id': content_type_id,
                        'perms_ids': {},
                        'perms': {}
                    }
                    obj[app_label][model]['perms'][perm] = permission_id
                    obj[app_label][model]['perms_ids'][permission_id] = perm
                else:
                    obj[app_label][model]['perms'][perm] = permission_id
                    obj[app_label][model]['perms_ids'][permission_id] = perm
            continue

        # If app_label does not exist yet
        if obj.get(app_label) is None:
            obj[app_label] = {}
            obj[app_label][model] = {
                'id': content_type_id,
                'perms_ids': {},
                'perms': {}
            }
            obj[app_label][model]['perms'][perm] = permission_id
            obj[app_label][model]['perms_ids'][permission_id] = perm
        else:
            # If model does not exist yet
            if obj.get(app_label).get(model) is None:
                obj[app_label][model] = {
                    'id': content_type_id,
                    'perms_ids': {},
                    'perms': {}
                }
                obj[app_label][model]['perms'][perm] = permission_id
                obj[app_label][model]['perms_ids'][permission_id] = perm
            else:
                if obj.get(app_label).get(model).get('perms').get(perm) is None:
                    obj[app_label][model]['perms'][perm] = permission_id
                    obj[app_label][model]['perms_ids'][permission_id] = perm

    return obj

def get_user_unique_permissions(user: CustomUser):
    """
        Returns a list of all the user's unique permissions either through groups 
        assigned to them or individual permissions
        [
            {
                "id": 28,
                "name": "Can view classification",
                "codename": "view_classification",
                "content_type": {
                    "id": 7,
                    "app_label": "demo",
                    "model": "classification"
                }
            },
            ...
    """
    # Get direct permissions and convert to a list to avoid uniqueness issues
    if user.is_superuser:
        user_permissions = list(Permission.objects.all())
    else:
        user_permissions = list(user.user_permissions.all())

    # Get permissions from groups and ensure uniqueness
    group_permissions = Permission.objects.filter(group__in=user.groups.all()).distinct()

    # Combine permissions
    all_permissions = user_permissions + list(group_permissions)

    # Remove duplicates (if any) using a set
    unique_permissions = {perm.id: perm for perm in all_permissions}.values()

    return unique_permissions