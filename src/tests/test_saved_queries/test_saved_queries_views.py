import pytest
from django.urls import reverse

from saved_queries.models import SavedQueryBuilder

data = {
    'name': 'myquery',
    "query": {
        "app_name": "demo",
        "model_name": "DemoModel",
        "conditions": [
            [
                "is_active", "equals", "True" 
            ],
            [
                "ordering", "lt", "12" 
            ]
        ],
        "orderings": [
            "ordering"
        ],
        "query_limit": None
    }
}

@pytest.fixture
def saved_query(db) -> SavedQueryBuilder:
    return SavedQueryBuilder.objects.create(
        name='saved_query',
        query=data.get('query')
    )


def test_query_builder_non_admin(api_client, non_admin_token):
    client = api_client()
    data = {}

    response = client.post(
        reverse(
            'query_builder', 
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401


def test_query_builder_invalid_body(api_client, limited_admin_token):
    client = api_client()
    data = {
        'invalid': 'body'
    }

    response = client.post(
        reverse(
            'query_builder', 
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 400


def test_query_builder_valid_body(api_client, limited_admin_token):
    client = api_client()
    data = {
        "app_name": "demo",
        "model_name": "DemoModel",
        "conditions": [
            [
                "is_active", "equals", "True" 
            ],
            [
                "ordering", "lt", "12" 
            ]
        ],
        "orderings": [
            "ordering"
        ],
        "query_limit": None
    }

    response = client.post(
        reverse(
            'query_builder', 
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 202
    data = response.data

    assert 'count' in data
    assert 'fields' in data
    assert 'results' in data


def test_raw_query_non_admin(api_client, non_admin_token):
    client = api_client()
    data = {}

    response = client.post(
        reverse(
            'raw_query', 
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401


def test_raw_query_non_superuser(api_client, limited_admin_token):
    client = api_client()
    data = {}

    response = client.post(
        reverse(
            'raw_query', 
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 403


def test_raw_query_invalid_body(api_client, superuser_token):
    client = api_client()
    data = {
        'invalid': 'body'
    }

    response = client.post(
        reverse(
            'raw_query', 
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 400


def test_raw_query_valid_body_invalid_query(api_client, superuser_token):
    client = api_client()
    data = {
        'query': 'DROP TABLE demo_demomodel;'
    }

    response = client.post(
        reverse(
            'raw_query', 
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 400


def test_raw_query_valid_body(api_client, superuser_token):
    client = api_client()
    data = {
        'query': 'SELECT 1;'
    }

    response = client.post(
        reverse(
            'raw_query', 
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 202
    data = response.data

    assert 'count' in data
    assert 'fields' in data
    assert 'results' in data


def test_get_all_query_builders_non_admin(api_client, non_admin_token):
    client = api_client()

    response = client.get(
        reverse(
            'get_all_query_builders', 
        ),
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_get_all_query_builders_non_superuser(api_client, limited_admin_token):
    client = api_client()

    response = client.get(
        reverse(
            'get_all_query_builders', 
        ),
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 403

def test_get_all_query_builders_valid(api_client, superuser_token):
    client = api_client()

    response = client.get(
        reverse(
            'get_all_query_builders', 
        ),
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 200

def test_add_query_builder_non_admin(api_client, non_admin_token):
    client = api_client()

    response = client.post(
        reverse(
            'add_query_builder', 
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_add_query_builder_non_superuser(api_client, limited_admin_token):
    client = api_client()

    response = client.post(
        reverse(
            'add_query_builder', 
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 403

def test_add_query_builder_invalid_body(api_client, superuser_token):
    client = api_client()
    invalid_data = {
        'name': 'myquery'
    }

    response = client.post(
        reverse(
            'add_query_builder', 
        ),
        data=invalid_data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 400

def test_add_query_builder_valid_body(api_client, superuser_token):
    client = api_client()

    response = client.post(
        reverse(
            'add_query_builder', 
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 201

def test_change_query_builder_non_admin(api_client, non_admin_token, saved_query):
    client = api_client()

    response = client.post(
        reverse(
            'change_query_builder', kwargs={'id': saved_query.pk}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_change_query_builder_non_superuser(api_client, limited_admin_token, saved_query):
    client = api_client()

    response = client.post(
        reverse(
            'change_query_builder', kwargs={'id': saved_query.pk}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 403

def test_change_query_builder_invalid_body(api_client, superuser_token, saved_query):
    client = api_client()
    invalid_data = {
        'name': 'myquery'
    }

    response = client.post(
        reverse(
            'change_query_builder', kwargs={'id': saved_query.pk}
        ),
        data=invalid_data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 400

def test_change_query_builder_not_existing(api_client, superuser_token):
    client = api_client()
    data['name'] = 'updated'

    response = client.post(
        reverse(
            'change_query_builder', kwargs={'id': 1111}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )

    assert response.status_code == 404

def test_change_query_builder_valid_body(api_client, superuser_token, saved_query):
    client = api_client()
    data['name'] = 'updated'

    response = client.post(
        reverse(
            'change_query_builder', kwargs={'id': saved_query.pk}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )

    assert response.status_code == 201

def test_delete_query_builder_non_admin(api_client, non_admin_token, saved_query):
    client = api_client()

    response = client.delete(
        reverse(
            'delete_query_builder', kwargs={'id': saved_query.pk}
        ),
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_delete_query_builder_non_superuser(api_client, limited_admin_token, saved_query):
    client = api_client()

    response = client.delete(
        reverse(
            'delete_query_builder', kwargs={'id': saved_query.pk}
        ),
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 403

def test_delete_query_builder_not_existing(api_client, superuser_token):
    client = api_client()

    response = client.delete(
        reverse(
            'delete_query_builder', kwargs={'id': 1111}
        ),
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 404

def test_delete_query_builder_valid_body(api_client, superuser_token, saved_query):
    client = api_client()

    response = client.delete(
        reverse(
            'delete_query_builder', kwargs={'id': saved_query.pk}
        ),
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )

    assert response.status_code == 202