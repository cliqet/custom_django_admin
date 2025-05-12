from django.urls import reverse


def test_get_model_docs_non_admin(api_client, non_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_model_docs'), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_get_model_docs_admin(api_client, superuser_token):
    client = api_client()

    response = client.get(
        reverse('get_model_docs'), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 200
    data = response.data
    
    assert 'docs' in data

