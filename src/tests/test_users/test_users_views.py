from django.urls import reverse


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

def test_get_user_detail_non_admin(api_client, non_admin_token, limited_admin):
    client = api_client()

    response = client.get(
        reverse('get_user_detail', kwargs={'uid': limited_admin.uid}),
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_get_user_detail_admin(api_client, superuser_token, limited_admin):
    client = api_client()

    response = client.get(
        reverse('get_user_detail', kwargs={'uid': limited_admin.uid}), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 200
    data = response.data
    
    assert 'user' in data
    assert data.get('user').get('uid') == limited_admin.uid

def test_get_user_permissions_non_admin(api_client, non_admin_token, limited_admin):
    client = api_client()

    response = client.get(
        reverse('get_user_permissions', kwargs={'uid': limited_admin.uid}),
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_get_user_permissions_admin(api_client, superuser_token, superuser):
    client = api_client()

    response = client.get(
        reverse('get_user_permissions', kwargs={'uid': superuser.uid}), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 200
    data = response.data
    
    assert 'permissions' in data

    first_key = next(iter(data.get('permissions')))
    first_obj = data.get('permissions').get(first_key)
    first_nested_key = next(iter(first_obj))
    first_nested_obj = first_obj.get(first_nested_key)

    assert 'perms_ids' in first_nested_obj
    assert 'perms' in first_nested_obj

def test_login_non_user(api_client, db):
    client = api_client()
    data = {
        'email': 'none@mail.com',
        'password': 'password123'
    }

    response = client.post(
        reverse('login'),
        data=data,
        format='json',
    )
    assert response.status_code == 401

def test_login_valid_user(api_client, superuser):
    client = api_client()

    data = {
        'email': superuser.email,
        'password': 'SomePassword1'
    }

    response = client.post(
        reverse('login'), 
        format='json',
        data=data,
    )
    assert response.status_code == 200
    data = response.data

    assert 'access' in data
    assert response.cookies.get('app.refresh_token') is not None

def test_send_password_reset_link_non_admin(api_client, limited_admin):
    client = api_client()

    response = client.get(
        reverse('send_password_reset_link', kwargs={'uid': limited_admin.uid}), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer invalidtoken'}
    )
    assert response.status_code == 401


def test_send_password_reset_link_admin(api_client, superuser_token, limited_admin):
    client = api_client()

    response = client.get(
        reverse('send_password_reset_link', kwargs={'uid': limited_admin.uid}), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 200
    data = response.data

    assert data.get('success')

def test_send_password_reset_link_admin_no_user(api_client, superuser_token):
    client = api_client()

    response = client.get(
        reverse('send_password_reset_link', kwargs={'uid': 'not_a_user'}), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 404
    