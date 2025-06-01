import pytest
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient

from backend.settings.base import APP_MODE, DjangoSettings
from django_admin.models.models_demo import Classification, DemoModel, Type
from django_admin.models.models_users import CustomUser, generate_user_id


@pytest.fixture(scope='session', autouse=True)
def check_django_settings_module():
    """
        Ensures that pytest runs when DJANGO_SETTINGS_MODULE=backend.settings.test
        PYTEST_MODE is True only when DJANGO_SETTINGS_MODULE = backend.settings.test
    """
    if APP_MODE != DjangoSettings.TEST:
        pytest.exit("""
            Set DJANGO_SETTINGS_MODULE value to backend.settings.test
        """)

@pytest.fixture(scope='session', autouse=True)
def setup():
    # Clear the cache at the start of the test
    cache.clear()

    # Do other setups here

    yield

    # Clear the cache at the end of the test
    cache.clear()

@pytest.fixture(scope='session')
def api_client():
    return APIClient

@pytest.fixture
def demo_permissions(db):
    # Get the content type for the DemoModel
    content_type = ContentType.objects.get_for_model(DemoModel)

    # Retrieve the add and view permissions for DemoModel
    add_permission = Permission.objects.get(codename='add_demomodel', content_type=content_type)
    view_permission = Permission.objects.get(codename='view_demomodel', content_type=content_type)

    return [add_permission, view_permission]

@pytest.fixture
def demo_model_group(demo_permissions):
    group = Group.objects.create(name='Demo Model Group')

    # Assign custom permissions to the group
    group.permissions.set(demo_permissions)  

    return group

@pytest.fixture
def user_factory(db):
    def create_user(
            email: str, 
            first_name: str, 
            last_name: str,
            is_active: bool = False,
            is_staff: bool = False,
            is_superuser: bool = False,
            permissions: list = [],
            groups: list = []):
        
        user = CustomUser.objects.create(
            uid=generate_user_id(),
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        user.set_password('SomePassword1')

        if permissions:
            user.user_permissions.set(permissions)

        if groups:
            user.groups.set(groups)
        
        user.save()

        return user
    return create_user


@pytest.fixture
def superuser(db, user_factory):
    return user_factory(
        'superuser@test.com',
        'Admin',
        'User',
        is_active=True,
        is_staff=True,
        is_superuser=True
    )

@pytest.fixture
def limited_admin(db, user_factory, demo_permissions, demo_model_group):
    return user_factory(
        'limitedadmin@test.com',
        'LimitedAdmin',
        'User',
        is_active=True,
        is_staff=True,
        permissions=[demo_permissions[1]],
        groups=[demo_model_group]
    )

@pytest.fixture
def inactive_admin(db, user_factory):
    return user_factory(
        'inactiveadmin@test.com',
        'InactiveAdmin',
        'User',
        is_staff=True,
    )

@pytest.fixture
def non_admin(db, user_factory):
    return user_factory(
        'oneadmin@test.com',
        'NoneAdmin',
        'User'
    )

@pytest.fixture
def superuser_token(api_client, superuser):
    client = api_client()

    data = {
        'email': superuser.email,
        'password': 'SomePassword1'
    }
    response = client.post(
        reverse('login'),
        data=data,
        format='json'
    )
    return response.data.get('access')

@pytest.fixture
def limited_admin_token(api_client, limited_admin):
    client = api_client()

    data = {
        'email': limited_admin.email,
        'password': 'SomePassword1'
    }
    response = client.post(
        reverse('login'),
        data=data,
        format='json'
    )

    return response.data.get('access')

@pytest.fixture
def non_admin_token(api_client, non_admin):
    client = api_client()
    
    data = {
        'email': non_admin.email,
        'password': 'SomePassword1'
    }

    response = client.post(
        reverse('login'),
        data=data,
        format='json',
    )

    return response.data.get('access')

@pytest.fixture
def type_instances(db):
        return [
            Type.objects.create(name='Success'),
            Type.objects.create(name='Danger'),
            Type.objects.create(name='Warning'),
        ]


@pytest.fixture
def classification_instances(db):
    return [
        Classification.objects.create(name='Class 1'),
        Classification.objects.create(name='Class 2'),
        Classification.objects.create(name='Class 3'),
    ]

@pytest.fixture
def sample_image_file():
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=b'file_content',  
        content_type='image/jpeg'
    )

@pytest.fixture
def sample_file():
    return SimpleUploadedFile(
        name='test_file.txt',
        content=b'This is a test file content.',
        content_type='text/plain'
    )


@pytest.fixture
def demo_model_factory(db, type_instances):
    def create_demo_model(
            name: str,
            email: str,
            color: str = 'Blue',
            ordering: int = 0,
            range_number: int = 5,
            amount: float = 0.0,
            comment: str = '',
            is_active: bool = True,
            date: str = '2023-01-01',
            time: str = '12:00:00',
            last_log: str = '2023-01-01T12:00:00Z',
            classifications: list = None,
            permissions: list = None,
            file: str = None,
            image: str = None,
            type_instance: Type = type_instances[0],
            metadata: dict = None,
            html: str = '<p>Sample HTML content</p>'
    ):

        demo_model = DemoModel.objects.create(
            name=name,
            email=email,
            color=color,
            ordering=ordering,
            range_number=range_number,
            amount=amount,
            comment=comment,
            is_active=is_active,
            date=date,
            time=time,
            last_log=last_log,
            type=type_instance,
            html=html,
            metadata=metadata or {},
            file=file,
            image=image
        )

        if classifications:
            demo_model.classification.set(classifications)

        if permissions:
            demo_model.permissions.set(permissions)

        return demo_model

    return create_demo_model

@pytest.fixture
def demo_model_instance(
    demo_model_factory, 
    sample_file, 
    sample_image_file, 
    demo_permissions,
    type_instances,
    classification_instances):
    return demo_model_factory(
        name='Demo Instance',
        email='demo@test.com',
        color='Blue',
        ordering=1,
        range_number=7,
        amount=100.0,
        comment='This is a demo comment.',
        is_active=True,
        date='2023-01-01',
        time='12:00:00',
        last_log='2023-01-01T12:00:00Z',
        classifications=classification_instances, 
        permissions=demo_permissions,     
        file=sample_file,          
        image=sample_image_file,        
        metadata={'key': 'value'},
        html='<p>Sample HTML content</p>'
    )