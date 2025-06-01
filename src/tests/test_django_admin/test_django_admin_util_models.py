import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.base import ModelBase

from django_admin.models.models_demo import DemoModel
from django_admin.utils_models import (
    _get_field_initial_data,
    _get_text_choices,
    _verbose_name_capitalize,
    build_filefield_helptext,
    get_converted_pk,
    get_model,
    get_model_fields_data,
    is_valid_modelfield_file,
)


def test_get_text_choices(demo_model_instance):
    fields = demo_model_instance._meta.get_fields()
    for field in fields:
        if not field.choices:
            assert _get_text_choices(field.choices) is None
        else:
            choices = _get_text_choices(field.choices)
            assert isinstance(choices, list)
            assert 'label' in choices[0]
            assert 'value' in choices[0]
            assert 'selected' in choices[0]

@pytest.mark.parametrize('text, expected', [
    ('HELLO', 'HELLO'),
    ('hello', 'Hello'),
    ('Hello', 'Hello'),
])
def test__verbose_name_capitalize(text, expected):
    result = _verbose_name_capitalize(text)
    assert result == expected

def test__get_field_initial_data(demo_model_instance):
    range_number = demo_model_instance._meta.get_field('range_number')
    data = _get_field_initial_data(range_number, False, None)
    assert data == range_number.default

    range_number = demo_model_instance._meta.get_field('range_number')
    data = _get_field_initial_data(range_number, True, demo_model_instance)
    assert data == demo_model_instance.range_number

def test_get_model_fields_data(demo_model_instance):
    demo_fields = [
        'id', 'type', 'color', 'name', 'email', 'ordering', 'range_number', 'amount',
        'comment', 'is_active', 'date', 'time', 'last_log', 'classification',
        'permissions', 'file', 'image', 'metadata', 'html', 'created_at', 'updated_at',
    ]
    data = get_model_fields_data(DemoModel)
    assert len(data) == len(demo_fields)
    assert 'manytomany_choices' in data.get('classification')
    assert 'manytomany_related_app' in data.get('permissions')
    assert 'manytomany_related_model' in data.get('permissions')
    assert 'foreignkey_choices' in data.get('type')
    assert 'foreignkey_model' in data.get('type')
    assert 'foreignkey_app' in data.get('type')
    assert 'value' in data.get('type').get('foreignkey_choices')[0]
    assert 'label' in data.get('type').get('foreignkey_choices')[0]
    assert 'selected' in data.get('type').get('foreignkey_choices')[0]
    assert 'regex_pattern' in data.get('amount')
    assert 'regex_message' in data.get('amount')
    assert 'min_value' in data.get('range_number')
    assert 'max_value' in data.get('range_number')

    data = get_model_fields_data(DemoModel, True, demo_model_instance)
    assert 'foreignkey_string' in data.get('type')

def test_get_model():
    model = get_model('django_admin.demomodel')
    assert isinstance(model, ModelBase)

def test_build_filefield_helptext():
    helptext = build_filefield_helptext(['.jpg', '.jpeg', '.png'], 2)
    assert helptext == "Allowed file types: ['.jpg', '.jpeg', '.png'] | Max file size in MB: [2]"

    helptext = build_filefield_helptext(max_file_size=2)
    assert helptext == "Allowed file types: [Any] | Max file size in MB: [2]"

    helptext = build_filefield_helptext(accepted_filetypes=['.jpg', '.jpeg', '.png'])
    assert helptext == "Allowed file types: ['.jpg', '.jpeg', '.png'] | Max file size in MB: [None]"

    helptext = build_filefield_helptext()
    assert helptext == "Allowed file types: [Any] | Max file size in MB: [None]"

def test_is_valid_modelfield_file():
    filefield_helptext = "Allowed file types: ['.jpg', '.jpeg'] | Max file size in MB: [2]"
    content_size = 1024 
    valid_size_content = b'0' * (content_size * 2)
    invalid_size_content = b'0' * (content_size * content_size * 2 + 1)  # 2mb + 1 byte

    valid_image = SimpleUploadedFile(
        name='test_image.jpg',
        content=valid_size_content,  
        content_type='image/jpeg'
    )
    result = is_valid_modelfield_file(filefield_helptext, valid_image)
    assert result.get('is_valid_type')
    assert result.get('is_valid_size')

    invalid_size_image = SimpleUploadedFile(
        name='test_image.jpg',
        content=invalid_size_content,  
        content_type='image/jpeg'
    )
    result = is_valid_modelfield_file(filefield_helptext, invalid_size_image)
    assert result.get('is_valid_type')
    assert not result.get('is_valid_size')

    invalid_type_image = SimpleUploadedFile(
        name='test_image.png',
        content=valid_size_content,  
        content_type='image/png'
    )
    result = is_valid_modelfield_file(filefield_helptext, invalid_type_image)
    assert not result.get('is_valid_type')
    assert result.get('is_valid_size')

    result = is_valid_modelfield_file('', invalid_type_image)
    assert result.get('is_valid_type')
    assert result.get('is_valid_size')

def test_get_converted_pk():
    pk = get_converted_pk('uid_123')
    assert isinstance(pk, str)

    pk = get_converted_pk(1)
    assert isinstance(pk, int)

    pk = get_converted_pk('1')
    assert isinstance(pk, int)