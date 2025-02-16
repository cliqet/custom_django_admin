from django.contrib.auth.models import Permission
from django.db.models import Q

from demo.models import DemoModel
from django_admin.serializers import PermissionSerializer
from django_admin.util_models import get_model_fields_data
from django_admin.utils import build_conditions_query, transform_conditions_query
from users.utils import get_user_unique_permissions, organize_permissions


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
    demo_model_permissions = permissions.get('demo').get('demomodel')
    
    assert 'perms_ids' in demo_model_permissions
    assert len(demo_model_permissions.get('perms_ids')) == 4
    assert len(demo_model_permissions.get('perms')) == 4


def test_transform_conditions_query(db):
    model_fields_data = get_model_fields_data(DemoModel)
    
    conditions = [
        ['is_active', 'equals', 'True'] 
    ]
    query = transform_conditions_query(conditions, model_fields_data)
    assert query[0][0] == 'is_active'
    assert query[0][1] == 'equals'
    assert query[0][2]
    assert isinstance(query[0][2], bool)

    conditions.append(['ordering', 'not_equals', '1'])
    query = transform_conditions_query(conditions, model_fields_data)
    assert query[1][2] == 1
    assert isinstance(query[1][2], int)

    conditions.append(['amount', 'equals', '20.03'])
    query = transform_conditions_query(conditions, model_fields_data)
    assert isinstance(query[2][2], float)

    conditions.append(['name', 'equals', 'Demo Name'])
    query = transform_conditions_query(conditions, model_fields_data)
    assert isinstance(query[3][2], str)


def test_build_conditions_query(db):
    model_fields_data = get_model_fields_data(DemoModel)

    conditions = [
        ['is_active', 'equals', 'True'] 
    ]
    transformed = transform_conditions_query(conditions, model_fields_data)
    query = build_conditions_query(transformed)
    assert query == Q(is_active=True)

    conditions.append(['amount', 'lt', '20.03'])
    transformed = transform_conditions_query(conditions, model_fields_data)
    query = build_conditions_query(transformed)
    assert query == Q(is_active=True) & Q(amount__lt=20.03)

    conditions.append(['name', 'not_equals', 'Demo Name'])
    transformed = transform_conditions_query(conditions, model_fields_data)
    query = build_conditions_query(transformed)
    assert query == Q(is_active=True) & Q(amount__lt=20.03) & ~Q(name='Demo Name')

    conditions = [['amount', 'lte', '20.03']]
    transformed = transform_conditions_query(conditions, model_fields_data)
    query = build_conditions_query(transformed)
    assert query == Q(amount__lte=20.03)

    conditions = [['amount', 'gt', '20.03']]
    transformed = transform_conditions_query(conditions, model_fields_data)
    query = build_conditions_query(transformed)
    assert query == Q(amount__gt=20.03)

    conditions = [['amount', 'gte', '20.03']]
    transformed = transform_conditions_query(conditions, model_fields_data)
    query = build_conditions_query(transformed)
    assert query == Q(amount__gte=20.03)
