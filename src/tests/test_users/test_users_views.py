from django.urls import reverse

from django_admin.constants import DASHBOARD_URL_PREFIX


def test_get_all_users_non_admin(api_client, non_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_all_users'), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_get_all_users_admin(api_client, superuser_token, limited_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_all_users'), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 200
    data = response.data
    
    assert 'users' in data
    assert len(data.get('users')) == 2