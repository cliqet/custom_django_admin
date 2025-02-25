from django.db.models import Q

from demo.models import DemoModel
from django_admin.util_models import get_model_fields_data
from saved_queries.utils import build_conditions_query, transform_conditions_query


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
