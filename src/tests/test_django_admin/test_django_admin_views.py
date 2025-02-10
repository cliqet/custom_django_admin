from django.urls import reverse

from django_admin.actions import CUSTOM_ACTIONS
from django_admin.constants import DASHBOARD_URL_PREFIX


def test_get_apps_non_admin(api_client, non_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_apps'), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_get_apps_admin(api_client, limited_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_apps'), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 200
    data = response.data
    
    assert 'appList' in data
    assert isinstance(data.get('appList'), list)

    model = data.get('appList')[0].get('models')[0]
    assert model.get('adminUrl').startswith(DASHBOARD_URL_PREFIX)
    assert model.get('addUrl').startswith(DASHBOARD_URL_PREFIX)

def test_get_model_fields_non_admin(api_client, non_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_model_fields', kwargs={'app_label': 'demo', 'model_name': 'demomodel'}), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_get_model_fields_admin(api_client, limited_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_model_fields', kwargs={'app_label': 'demo', 'model_name': 'demomodel'}), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 200
    data = response.data

    assert 'fields' in data
    
    first_key = next(iter(data.get('fields')))
    first_obj = data.get('fields').get(first_key)
    assert 'name' in first_obj
    assert 'label' in first_obj
    assert 'is_primary_key' in first_obj
    assert 'max_length' in first_obj
    assert 'editable' in first_obj
    assert 'help_text' in first_obj
    assert 'auto_created' in first_obj
    assert 'type' in first_obj
    assert 'initial' in first_obj
    assert 'required' in first_obj
    assert 'choices' in first_obj

def test_get_model_fields_admin_not_found(api_client, limited_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_model_fields', kwargs={'app_label': 'demo', 'model_name': 'nothing'}), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 404

def test_get_model_admin_settings_non_admin(api_client, non_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_model_admin_settings', kwargs={'app_label': 'demo', 'model_name': 'demomodel'}), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_get_model_admin_settings_admin(api_client, limited_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_model_admin_settings', kwargs={'app_label': 'demo', 'model_name': 'demomodel'}), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 200
    data = response.data

    assert 'model_admin_settings' in data
    admin_settings = data.get('model_admin_settings')
    assert 'model_name' in admin_settings
    assert isinstance(admin_settings.get('model_name'), str)
    assert 'app_label' in admin_settings
    assert isinstance(admin_settings.get('app_label'), str)
    assert 'fieldsets' in admin_settings
    assert isinstance(admin_settings.get('fieldsets'), list)
    assert 'list_per_page' in admin_settings
    assert isinstance(admin_settings.get('list_per_page'), int)
    assert 'list_filter' in admin_settings
    assert isinstance(admin_settings.get('list_filter'), list)
    assert 'list_display' in admin_settings
    assert isinstance(admin_settings.get('list_display'), list)
    assert 'list_display_links' in admin_settings
    assert isinstance(admin_settings.get('list_display_links'), list)
    assert 'search_fields' in admin_settings
    assert isinstance(admin_settings.get('search_fields'), list)
    assert 'search_help_text' in admin_settings
    assert isinstance(admin_settings.get('search_help_text'), str)
    assert 'ordering' in admin_settings
    assert isinstance(admin_settings.get('ordering'), list)
    assert 'autocomplete_fields' in admin_settings
    assert isinstance(admin_settings.get('autocomplete_fields'), list)
    assert 'readonly_fields' in admin_settings
    assert isinstance(admin_settings.get('readonly_fields'), list)
    assert 'custom_actions' in admin_settings
    assert isinstance(admin_settings.get('custom_actions'), list)
    assert 'custom_inlines' in admin_settings
    assert isinstance(admin_settings.get('custom_inlines'), list)
    assert 'extra_inlines' in admin_settings
    assert isinstance(admin_settings.get('extra_inlines'), list)
    assert 'table_filters' in admin_settings
    assert isinstance(admin_settings.get('table_filters'), list)
    assert 'func' in admin_settings.get('custom_actions')[0]
    assert 'label' in admin_settings.get('custom_actions')[0]

def test_get_model_admin_settings_admin_not_found(api_client, limited_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_model_admin_settings', kwargs={'app_label': 'demo', 'model_name': 'nothing'}), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 404

def test_get_model_fields_edit_non_admin(api_client, non_admin_token, demo_model_instance):
    client = api_client()

    response = client.get(
        reverse(
            'get_model_fields_edit', 
            kwargs={'app_label': 'demo', 'model_name': 'demomodel', 'pk': demo_model_instance.pk}
        ), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_get_model_fields_edit_admin(api_client, superuser_token, demo_model_instance):
    client = api_client()

    response = client.get(
        reverse(
            'get_model_fields_edit', 
            kwargs={'app_label': 'demo', 'model_name': 'demomodel', 'pk': demo_model_instance.pk}
        ), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 200
    data = response.data

    assert 'fields' in data
    
    first_key = next(iter(data.get('fields')))
    first_obj = data.get('fields').get(first_key)
    assert 'name' in first_obj
    assert 'label' in first_obj
    assert 'is_primary_key' in first_obj
    assert 'max_length' in first_obj
    assert 'editable' in first_obj
    assert 'help_text' in first_obj
    assert 'auto_created' in first_obj
    assert 'type' in first_obj
    assert 'initial' in first_obj
    assert 'required' in first_obj
    assert 'choices' in first_obj

    field_value = getattr(demo_model_instance, first_key, None)
    assert first_obj.get('initial') == field_value 

def test_get_model_fields_edit_admin_not_found(api_client, superuser_token):
    client = api_client()

    response = client.get(
        reverse(
            'get_model_fields_edit', 
            kwargs={'app_label': 'demo', 'model_name': 'demomodel', 'pk': 1000}
        ), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 404

def test_get_model_fields_edit_admin_no_permission(api_client, limited_admin_token):
    client = api_client()

    response = client.get(
        reverse(
            'get_model_fields_edit', 
            kwargs={'app_label': 'demo', 'model_name': 'demomodel', 'pk': 1000}
        ), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 403

def test_get_permissions_non_admin(api_client, non_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_permissions'), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_get_permissions_admin(api_client, limited_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_permissions'), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 200
    data = response.data

    assert 'permissions' in data

def test_get_content_types_non_admin(api_client, non_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_content_types'), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_get_content_types_admin(api_client, limited_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_content_types'), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 200
    data = response.data

    assert 'contentTypes' in data

def test_get_groups_non_admin(api_client, non_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_groups'), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_get_groups_admin(api_client, superuser_token):
    client = api_client()

    response = client.get(
        reverse('get_groups'), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 200
    data = response.data

    assert 'groups' in data

def test_get_groups_admin_no_permission(api_client, limited_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_groups'), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 403

def test_get_log_entries_non_admin(api_client, non_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_log_entries'), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_get_log_entries_admin(api_client, superuser_token):
    client = api_client()

    response = client.get(
        reverse('get_log_entries'), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 200
    data = response.data

    assert 'logEntries' in data

def test_get_log_entries_admin_no_permission(api_client, limited_admin_token):
    client = api_client()

    response = client.get(
        reverse('get_log_entries'), 
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 403

def test_get_model_record_non_admin(api_client, non_admin_token, demo_model_instance):
    client = api_client()
    
    response = client.get(
        reverse(
            'get_model_record', 
            kwargs={'app_label': 'demo', 'model_name': 'demomodel', 'pk': demo_model_instance.pk}
        ),
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_get_model_record_admin(api_client, superuser_token, demo_model_instance):
    client = api_client()

    response = client.get(
        reverse(
            'get_model_record', 
            kwargs={'app_label': 'demo', 'model_name': 'demomodel', 'pk': demo_model_instance.pk}
        ),  
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 200
    data = response.data

    assert 'record' in data

def test_get_model_listview_non_admin(api_client, non_admin_token):
    client = api_client()
    
    response = client.get(
        reverse(
            'get_model_listview', 
            kwargs={'app_label': 'demo', 'model_name': 'demomodel'}
        ),
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_get_model_listview_admin(api_client, superuser_token):
    client = api_client()
    
    response = client.get(
        reverse(
            'get_model_listview', 
            kwargs={'app_label': 'demo', 'model_name': 'demomodel'}
        ),
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 200
    data = response.data

    assert 'count' in data
    assert 'next' in data
    assert 'previous' in data
    assert 'results' in data

def test_get_model_listview_admin_no_permission(api_client, limited_admin_token):
    client = api_client()
    
    response = client.get(
        reverse(
            'get_model_listview', 
            kwargs={'app_label': 'auth', 'model_name': 'group'}
        ),
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 403

def test_get_inline_listview_non_admin(api_client, non_admin_token):
    client = api_client()
    
    response = client.get(
        reverse(
            'get_inline_listview', 
            kwargs={'parent_app_label': 'demo', 'parent_model_name': 'demomodel'}
        ),
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_custom_action_delete_non_admin(api_client, non_admin_token):
    client = api_client()
    data = {
        'payload': [1]
    }
    
    response = client.post(
        reverse(
            'custom_action_view', 
            kwargs={'app_label': 'demo', 'model_name': 'demomodel', 'func': CUSTOM_ACTIONS.DELETE_LISTVIEW.value}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_custom_action_delete_admin_invalid_payload(api_client, superuser_token):
    client = api_client()
    data = {
        'invalid_payload': [1]
    }
    
    response = client.post(
        reverse(
            'custom_action_view', 
            kwargs={'app_label': 'demo', 'model_name': 'demomodel', 'func': CUSTOM_ACTIONS.DELETE_LISTVIEW.value}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 400

    data = {
        'payload': 'invalid'
    }
    
    response = client.post(
        reverse(
            'custom_action_view', 
            kwargs={'app_label': 'demo', 'model_name': 'demomodel', 'func': CUSTOM_ACTIONS.DELETE_LISTVIEW.value}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 400

def test_custom_action_delete_admin_no_permission(api_client, limited_admin_token):
    client = api_client()
    data = {
        'payload': [1]
    }
    
    response = client.post(
        reverse(
            'custom_action_view', 
            kwargs={'app_label': 'demo', 'model_name': 'demomodel', 'func': CUSTOM_ACTIONS.DELETE_LISTVIEW.value}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 403

def test_custom_action_delete_admin_valid_delete(api_client, superuser_token):
    client = api_client()
    data = {
        'payload': [1]
    }
    
    response = client.post(
        reverse(
            'custom_action_view', 
            kwargs={'app_label': 'demo', 'model_name': 'demomodel', 'func': CUSTOM_ACTIONS.DELETE_LISTVIEW.value}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 202
    data = response.data

    assert data.get('message') == 'Deleted 1 record/s successfully'

def test_add_model_record_non_admin(api_client, non_admin_token):
    client = api_client()
    data = {
        'name': 'Test Country' 
    }
    
    response = client.post(
        reverse(
            'add_model_record', 
            kwargs={'app_label': 'demo', 'model_name': 'country'}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_add_model_record_admin_no_permission(api_client, limited_admin_token):
    client = api_client()
    data = {
        'name': 'Test Country' 
    }
    
    response = client.post(
        reverse(
            'add_model_record', 
            kwargs={'app_label': 'demo', 'model_name': 'country'}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 403

def test_add_model_record_admin_invalid_body(api_client, superuser_token):
    client = api_client()
    data = {
        'invalid': 'Test Country' 
    }
    
    response = client.post(
        reverse(
            'add_model_record', 
            kwargs={'app_label': 'demo', 'model_name': 'country'}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 400

def test_add_model_record_admin_valid_body(api_client, superuser_token):
    client = api_client()
    data = {
        'name': 'Test Country' 
    }
    
    response = client.post(
        reverse(
            'add_model_record', 
            kwargs={'app_label': 'demo', 'model_name': 'country'}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 201

def test_change_model_record_non_admin(api_client, non_admin_token, type_instances):
    client = api_client()
    data = {
        'name': 'Changed'
    }
    
    response = client.post(
        reverse(
            'change_model_record', 
            kwargs={'app_label': 'demo', 'model_name': 'type', 'pk': type_instances[0].pk}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_change_model_record_admin_no_permission(api_client, limited_admin_token, type_instances):
    client = api_client()
    data = {
        'name': 'Changed'
    }
    
    response = client.post(
        reverse(
            'change_model_record', 
            kwargs={'app_label': 'demo', 'model_name': 'type', 'pk': type_instances[0].pk}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 403

def test_change_model_record_admin_invalid_body(api_client, superuser_token, type_instances):
    client = api_client()
    data = {
        'invalid': 'body'
    }

    
    response = client.post(
        reverse(
            'change_model_record', 
            kwargs={'app_label': 'demo', 'model_name': 'type', 'pk': type_instances[0].pk}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 400

def test_change_model_record_admin_valid(api_client, superuser_token, type_instances):
    client = api_client()
    data = {
        'name': 'Changed'
    }
    
    response = client.post(
        reverse(
            'change_model_record', 
            kwargs={'app_label': 'demo', 'model_name': 'type', 'pk': type_instances[0].pk}
        ),
        data=data,
        format='json',
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 201

def test_delete_model_record_non_admin(api_client, non_admin_token, type_instances):
    client = api_client()

    response = client.delete(
        reverse(
            'delete_model_record', 
            kwargs={'app_label': 'demo', 'model_name': 'type', 'pk': type_instances[0].pk}
        ),
        **{'HTTP_AUTHORIZATION': f'Bearer {non_admin_token}'}
    )
    assert response.status_code == 401

def test_delete_model_record_admin_no_permission(api_client, limited_admin_token, type_instances):
    client = api_client()

    response = client.delete(
        reverse(
            'delete_model_record', 
            kwargs={'app_label': 'demo', 'model_name': 'type', 'pk': type_instances[0].pk}
        ),
        **{'HTTP_AUTHORIZATION': f'Bearer {limited_admin_token}'}
    )
    assert response.status_code == 403

def test_delete_model_record_admin_valid(api_client, superuser_token, type_instances):
    client = api_client()

    response = client.delete(
        reverse(
            'delete_model_record', 
            kwargs={'app_label': 'demo', 'model_name': 'type', 'pk': type_instances[0].pk}
        ),
        **{'HTTP_AUTHORIZATION': f'Bearer {superuser_token}'}
    )
    assert response.status_code == 202