import pytest

from django_admin.data_transform import (
    destructure_dict,
    destructure_list,
    to_camel_case,
    to_snake_case,
    transform_dict_to_camel_case,
    transform_dict_to_snake_case,
)


def double(num: int | float) -> int | float:
        return num * 2


@pytest.mark.parametrize('camel_case_str, expected', [
    ('helloWorld', 'hello_world'),
    ('helloWorldToday', 'hello_world_today'),
    ('world', 'world'),
    (1, 1),
    (True, True)
])
def test_to_snake_case(camel_case_str, expected):
    result = to_snake_case(camel_case_str)
    assert result == expected


@pytest.mark.parametrize('snake_str, expected', [
    ('hello_world', 'helloWorld'),
    ('hello_world_today', 'helloWorldToday'),
    ('world', 'world'),
    (1, 1),
    (True, True)
])
def test_to_camel_case(snake_str, expected):
    result = to_camel_case(snake_str)
    assert result == expected


def test_transform_dict_to_camel_case():
    dict_obj = {
        'page': {
            'page_name': 'home',
            'ordered_components': [
                {
                    'ordered_texts': [{'text_name': 'Some text'}], 
                    'ordered_images': []
                }
            ]
        }
    }

    expected = {
        'page': {
            'pageName': 'home',
            'orderedComponents': [
                {
                    'orderedTexts': [{'textName': 'Some text'}], 
                    'orderedImages': []
                }
            ]
        }
    }

    assert transform_dict_to_camel_case(dict_obj) == expected


def test_transform_dict_to_snake_case():
    dict_obj = {
        'page': {
            'pageName': 'home',
            'orderedComponents': [
                {
                    'orderedTexts': [{'textName': 'Some text'}], 
                    'orderedImages': []
                }
            ]
        }
    }

    expected = {
        'page': {
            'page_name': 'home',
            'ordered_components': [
                {
                    'ordered_texts': [{'text_name': 'Some text'}], 
                    'ordered_images': []
                }
            ]
        }
    }

    assert transform_dict_to_snake_case(dict_obj) == expected


def test_destructure_list():
    arr = [1, 2, 3, 4, 5]
    a, b, c = destructure_list(arr, ['a', 'b', 'c'])
    assert a == 1
    assert b == 2
    assert c == 3

    a, b, c = destructure_list(arr, ['a', 'b', '...rest'])
    assert a == 1
    assert b == 2
    assert c == [3, 4, 5]

    a, b = destructure_list(arr, ['a', '_', '...rest'])
    assert a == 1
    assert b == [3, 4, 5]

    a, b, c = destructure_list(arr, ['a', 'b', '...rest'], [double, double, sum])
    assert a == 2
    assert b == 4
    assert c == 12


def test_destructure_dict():
    dict_obj = {
        'name': 'mike',
        'password_changes': 23,
        'passwords_used': ['pass1', 'pass3', 'pass4'],
        'password': {
            'value': 'CompanyA',
            'secure': False
        }
    }
    password_changes, password_length = destructure_dict(
         dict_obj, 
         ['password_changes', 'password->value'], 
         apply_funcs=[double, len]
    )
    assert password_changes == 46
    assert password_length == 8