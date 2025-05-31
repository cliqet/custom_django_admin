import re
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Literal

from django.apps import apps
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import (
    DecimalValidator,
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models
from django.db.models import Field, ForeignObjectRel

PK_FIELD = Literal['pk', 'id']


def _get_text_choices(field_choices: list[tuple] | None) -> list[dict] | None:
    if not field_choices:
        return None

    return [
        {
            'label': choice[1],
            'value': choice[0],
            'selected': False if index != 0 else True,
        }
        for index, choice in enumerate(field_choices)
    ]


def _verbose_name_capitalize(text: str) -> str:
    if text.isupper():
        return text
    return text.title()

def get_pk_or_id_value(obj) -> Any:
    try:
        return getattr(obj, 'pk')
    except Exception:
        return getattr(obj, 'id')
    
def get_pk_field(obj) -> PK_FIELD:
    try:
        obj.pk
        return 'pk'
    except Exception:
        return 'id'

def _get_field_initial_data(field, is_edit: bool, instance):
    """
        Gets a model field's initial data. Uses default field value on add mode.
        Uses field values if on edit mode.
    """
    if not is_edit and not instance:
        return field.get_default() if field.name != 'uid' else ''
    else:
        if isinstance(field, models.ForeignKey) or isinstance(field, models.OneToOneField):
            related_instance = getattr(instance, field.name)
            return get_pk_or_id_value(related_instance) if related_instance else None
        else:
            value = getattr(instance, field.name)
            if isinstance(value, (datetime, date, time)):
                return value.isoformat()
            elif isinstance(value, Decimal):
                return str(value)
            elif isinstance(field, models.ManyToManyField):
                related_instances = getattr(instance, field.name).all()
                return [related_instance.pk for related_instance in related_instances]
            elif isinstance(field, (models.FileField, models.ImageField)):
                if value:
                    return value.url
                return None
            return value

def is_model_field(field) -> bool:
    """
        Checks if the field is defined in the model including inheritance 
        but not reverse relationships since model._meta.get_fields()
        returns those as well
    """
    if isinstance(field, (models.ManyToOneRel, models.ManyToManyRel)):
        return False
    return True


def get_model_fields_data(model: models.Model, is_edit: bool = False, instance = None) -> dict:
    """ Gets all fields of a model and their attributes. Used in model forms """
    model_fields: list[Field[Any, Any] | ForeignObjectRel] = model._meta.get_fields()

    field_names: dict = {}
    for field in model_fields:  
        if not is_model_field(field):
            continue
        initial_data = _get_field_initial_data(field, is_edit, instance)

        if field.concrete:
            field_names[field.name] = {
                'name': field.name,
                'label': _verbose_name_capitalize(field.verbose_name),
                'is_primary_key': field.primary_key,
                'max_length': field.max_length,
                'editable': field.editable,
                'help_text': field.help_text,
                'auto_created': field.auto_created,
                'type': field.__class__.__name__,
                'initial': initial_data,
                'required': not field.blank,
                # choices is returned as a list of list like [['db_value', 'UI_VALUE'], ...]
                'choices': _get_text_choices(field.choices),
            }

        # Check if it's a ManyToManyField
        if isinstance(field, models.ManyToManyField):
            # Get all available options for selection
            if not is_edit:
                all_choices = [
                    {
                        'id': get_pk_or_id_value(obj),
                        'label': str(obj),
                        'checked': False
                    } 
                    for obj in field.remote_field.model.objects.all()
                ]
            else:
                # use the existing value as the selected one
                all_choices = [
                    {
                        'id': get_pk_or_id_value(obj),
                        'label': str(obj),
                        'checked': True if get_pk_or_id_value(obj) in initial_data else False
                    } 
                    for obj in field.remote_field.model.objects.all()
                ]
            field_names[field.name]['manytomany_choices'] = all_choices
            field_names[field.name]['manytomany_related_app'] = field.remote_field.model._meta.app_label
            field_names[field.name]['manytomany_related_model'] = field.remote_field.model.__name__

        # Check if it's a foreign key
        is_select_field = isinstance(field, models.ForeignKey) or isinstance(field, models.OneToOneField)
        if is_select_field:
            # Get all available options for selection
            if not initial_data:
                all_choices = [
                    {
                        'value': get_pk_or_id_value(obj),
                        'label': str(obj),
                        'selected': False if index != 0 else True
                    } 
                    for index, obj in enumerate(field.remote_field.model.objects.all())
                ]
            else:
                if is_edit:
                    # use the existing value as the selected one
                    all_choices = [
                        {
                            'value': get_pk_or_id_value(obj),
                            'label': str(obj),
                            'selected': True if initial_data == get_pk_or_id_value(obj) else False
                        } 
                        for index, obj in enumerate(field.remote_field.model.objects.all())
                    ]
                else:
                    all_choices = [
                        {
                            'value': get_pk_or_id_value(obj),
                            'label': str(obj),
                            'selected': False if index != 0 else True
                        } 
                        for index, obj in enumerate(field.remote_field.model.objects.all())
                    ]

            field_names[field.name]['foreignkey_choices'] = all_choices
            field_names[field.name]['foreignkey_model'] = field.remote_field.model.__name__
            field_names[field.name]['foreignkey_app'] = field.remote_field.model._meta.app_label

            related_model = field.remote_field.model
            pk_field = get_pk_field(related_model)
            field_names[field.name]['foreignkey_string'] = field.remote_field.model.objects.filter(**{
                pk_field: initial_data
            }).first().__str__()
                
        try:
            for validator in field.validators:
                if isinstance(validator, RegexValidator):
                    regex_data = validator._constructor_args[1]
                    field_names[field.name]['regex_pattern'] = regex_data.get('regex')
                    field_names[field.name]['regex_message'] = regex_data.get('message')
                if isinstance(validator, MinValueValidator):
                    field_names[field.name]['min_value'] = validator.limit_value
                if isinstance(validator, MaxValueValidator):
                    field_names[field.name]['max_value'] = validator.limit_value
                if isinstance(validator, DecimalValidator):
                    field_names[field.name]['max_digits'] = field.max_digits
                    field_names[field.name]['decimal_places'] = field.decimal_places
                # Add other custom validators here
        except AttributeError:
            ...

    return field_names


def get_model(model_identifier: str) -> models.base.ModelBase:
    """ Look up a model from an "app_label.model_name" string. """
    return apps.get_model(model_identifier)


def build_filefield_helptext(accepted_filetypes: list[str] = [], max_file_size: int | None = None) -> str:
    """
        Builds the help text for file validation which is parsed by the frontend to create
        the rules on the frontend side.
        @param accepted_filetypes is list of file type extensions such as .jpg, .png, etc.
        @param max_file_size is the limit in MB
    """
    file_types = str(accepted_filetypes) if accepted_filetypes else '[Any]'
    file_size = max_file_size or 'None'

    return f'Allowed file types: {file_types} | Max file size in MB: [{file_size}]'


def is_valid_modelfield_file(filefield_helptext: str, file: InMemoryUploadedFile) -> dict:
    """
        Checks whether a file is valid based on help text where limits are set
        Returns {
            'is_valid_type': True,
            'is_valid_size': True,
        }
    """
    if not filefield_helptext:
        return {
            'is_valid_type': True,
            'is_valid_size': True,
        }
    
    is_valid_type = False
    is_valid_size = False
    
    # Split the help text into file type and file size phrases
    filetype_phrase, filesize_phrase = filefield_helptext.split('|')

    # Regular expression to match content within square brackets
    regex_pattern = r'\[(.*?)\]'

    # Extract file types
    filetype_match = re.search(regex_pattern, filetype_phrase)

    if filetype_match:
        filetypes = filetype_match.group(1).split(',')
        filetypes = [item.strip().replace("'", "") for item in filetypes]

        # If any file type is allowed
        if filetypes and filetypes[0] == 'Any':
            is_valid_type = True

        # If certain file types only are allowed
        if filetypes and filetypes[0] != 'Any':
            file_extension = file.name.split('.')[-1].lower()  # Get the file extension
            if f'.{file_extension}' in filetypes:
                is_valid_type = True

    filesize_match = re.search(regex_pattern, filesize_phrase)

    if filesize_match:
        size_limit_in_mb = filesize_match.group(1).strip()

        # If there is no size limit
        if size_limit_in_mb.lower() == "none":
            is_valid_size = True
        else:
            # If there is a size limit
            file_size_in_mb = file.size / (1024 ** 2)
            if file_size_in_mb <= int(size_limit_in_mb):
                is_valid_size = True

    return {
        'is_valid_type': is_valid_type,
        'is_valid_size': is_valid_size,
    }

def get_converted_pk(pk: str | int) -> str | int:
    # Convert pk to an int if pk is a number
    # If it fails, then it must be a uid or a string type of pk
    try:
        converted_pk = int(pk)
    except Exception:
        converted_pk = pk

    return converted_pk

