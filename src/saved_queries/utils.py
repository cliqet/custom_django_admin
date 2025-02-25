from typing import Any

from django.db.models import Q


def build_conditions_query(conditions: list[list[str | Any]]):
    query = None  
    for condition in conditions:
        field, operator, value = condition
        
        if operator == 'equals':
            current_query = Q(**{field: value})
        elif operator == 'not_equals':
            current_query = Q(**{field: value})  
            current_query = ~current_query  
        elif operator == 'gte':
            current_query = Q(**{f"{field}__gte": value})
        elif operator == 'gt':
            current_query = Q(**{f"{field}__gt": value})
        elif operator == 'lte':
            current_query = Q(**{f"{field}__lte": value})
        elif operator == 'lt':
            current_query = Q(**{f"{field}__lt": value})

        if query is None:
            query = current_query
        else:
            query &= current_query

    return query

def transform_conditions_query(
        conditions: list[list[str | Any]], 
        model_fields_data: dict) -> list[list[str | Any]]:
    """
        Transforms the conditions query to proper values
    """
    transform_conditions = []
    for condition in conditions:
        field, operator, value = condition

        field_data = model_fields_data.get(field)
        if field_data.get('type') == 'BooleanField':
            value = bool(value)
        elif field_data.get('type') in ['IntegerField', 'PositiveIntegerField', 'PositiveSmallIntegerField']:
            value = int(value)
        elif field_data.get('type') == 'DecimalField':
            value = float(value)

        transform_conditions.append([field, operator, value])

    return transform_conditions