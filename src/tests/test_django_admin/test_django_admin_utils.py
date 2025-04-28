from django.contrib.auth.models import Permission

from django_admin.serializers import PermissionSerializer
from django_admin_users.utils import get_user_unique_permissions, organize_permissions


def test_get_user_unique_permissions(superuser, limited_admin, demo_permissions):
    all_permissions = Permission.objects.all()
    user_permissions = get_user_unique_permissions(superuser)
    assert len(user_permissions) == len(all_permissions)

    limited_permissions = get_user_unique_permissions(limited_admin)
    assert len(limited_permissions) == len(demo_permissions)


def test_organize_permissions(superuser):
    user_permissions = get_user_unique_permissions(superuser)
    serialized_permissions = PermissionSerializer(user_permissions, many=True).data
    permissions = organize_permissions(serialized_permissions, superuser)
    demo_model_permissions = permissions.get('django_admin_demo').get('demomodel')
    
    assert 'perms_ids' in demo_model_permissions
    assert len(demo_model_permissions.get('perms_ids')) == 4
    assert len(demo_model_permissions.get('perms')) == 4


