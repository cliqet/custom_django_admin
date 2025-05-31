from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Tuple, TypeVar
from uuid import uuid4

from django.db import models, transaction
from django.db.models import ForeignKey, Max, Model
from django.http.request import HttpRequest

from django_admin.admin.admin_main import BaseModelAdmin
from django_admin.serializers import AdminCustomInlineSerializer

from .utils_models import get_model


@dataclass
class ModelCreationData:
    """
    Stores the temporary records for creation of the instance"s copy along with data needed 
    to associate fk relationships and m2m relationships
    """
    class_model: Model
    model_ref_uid: str
    model_fields: dict
    m2m_fields: dict
    has_recursive_parent_instance: bool
    fks_to_last_parent_instance: list[dict] = field(default_factory=list)


ModelInstanceType = TypeVar('ModelInstanceType', bound=models.Model)


def get_model_perm(permission_code_name: str, model_name: str) -> str:
    return permission_code_name.replace(f'_{model_name}', '')


def serialize_model_admin(app_label: str, model: Model, model_admin: BaseModelAdmin) -> dict:
    """
        Serializes the model admin settings
    """
    if not model_admin:
        return None

    serialized_data = {
        'model_name': model.__name__,
        'app_label': app_label,
        'fieldsets': [],
        'list_display': model_admin.list_display,
        'list_per_page': model_admin.list_per_page,
        'list_display_links': model_admin.list_display_links,
        'search_fields': model_admin.search_fields,
        'search_help_text': model_admin.search_help_text,
        'list_filter': model_admin.list_filter,
        'readonly_fields': model_admin.readonly_fields,
        'ordering': model_admin.ordering,
        'custom_actions': model_admin.custom_actions,
        'autocomplete_fields': model_admin.autocomplete_fields,
        'table_filters': model_admin.table_filters,
        'custom_inlines': AdminCustomInlineSerializer(
            model_admin.get_custom_inlines(),
            many=True
        ).data,
        'extra_inlines': model_admin.extra_inlines,
        'custom_change_link': model_admin.custom_change_link
    }

    pk_field = model._meta.pk.name

    # If there is no list display
    if not model_admin.list_display:
        serialized_data['list_display'] = [pk_field]

    # If list_display_links is not defined, make pk field name the default
    if not model_admin.list_display_links:
        # Just use the first in list display
        if pk_field not in serialized_data['list_display']:
            serialized_data['list_display_links'] = [serialized_data['list_display'][0]]
        else:
            serialized_data['list_display_links'] = [model._meta.pk.name]

    if not model_admin.search_fields:
        serialized_data['search_help_text'] = 'Search not available'

    if model_admin.list_filter:
        table_filters = []
        for field in model_admin.list_filter:
            table_filter_fields = {}
            table_filter_fields['field'] = field
            field_object = model._meta.get_field(field)
            initial_unique_field_values = [{'value': None, 'label': 'All'}]

            if isinstance(field_object, ForeignKey):
                related_model = field_object.related_model
                unique_related_instances = related_model.objects.distinct()
                unique_field_values = [
                    { 'value': instance.pk, 'label': str(instance)}
                    for instance in unique_related_instances
                ]
            elif field_object.choices:
                unique_field_values = [
                    {'value': val, 'label': label}
                    for val, label in field_object.choices
                ]
            else:
                unique_values = model.objects.values_list(field, flat=True).distinct()
                unique_field_values = [
                    {'value': val, 'label': str(val)}  
                    for val in unique_values
                ]
            table_filter_fields['values'] = initial_unique_field_values + unique_field_values
            table_filters.append(table_filter_fields)
        serialized_data['table_filters'] = table_filters

    # Organize and serialize fieldsets
    if model_admin.fieldsets:
        for title, options in model_admin.fieldsets:
            serialized_data['fieldsets'].append({
                'title': title,
                'fields': options['fields']
            })
    # If no fieldsets are defined in the model admin
    # Get all fields defined in the model
    else:
        serialized_data['fieldsets'].append({
            'title': 'Fields',
            'fields': [
                field.name for field in model._meta.get_fields()
                if (field.model == model and not field.auto_created) or field.name == 'id'
            ]
        })

    return serialized_data

def get_client_ip(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

def get_model_defined_field_value(field, instance) -> Tuple[bool, Any]:
    """
        Checks if the field is defined in the model including inherited fields
        from another model but not include reverse relationships since 
        model._meta.get_fields() returns those as well. E.g. you may have
        class ModelA(models.Model):
            name = models.CharField(...)
            age = models.IntegerField(...)
        name and age are fields defined in the model but because Django creates 
        reverse relationships, this will appear in model._meta.get_fields().
        Exceptions to the reverse relationships are when you define a related_name 
        attribute to the model field of the related model. E.g. 
        class ModelB(models.Model):
            model_a = models.ForeignKey(ModelA, related_name=model_b_instances)
        Since model_a has the related_name, this reverse relationship between ModelA and 
        ModelB will be included. Therefore, this function will return True. 
        So, if you want to include in copying the related models, you need to set a 
        related_name attribute to the model field
        Returns True if it is a model defined field and the value of the field
    """
    value = getattr(instance, field.name, "NOT_A_MODEL_FIELD")
    return value != "NOT_A_MODEL_FIELD", value

def is_number_type_field(field_type) -> bool:
    if field_type in ["IntegerField", "PositiveIntegerField", "DecimalField"]:
        return True
    return False

def has_model_method(instance: ModelInstanceType, method_name: str) -> bool:
    return hasattr(instance, method_name) and callable(getattr(instance, method_name))


def copy_record(
    instance: ModelInstanceType, 
    set_field_values: Dict[str, Callable[..., Any]] = {}
) -> list[str]:
    """
        NOTE: If you want to copy related instances, set a related_name attribute 
        on the field that relates to the model of the instance being copied.
        Otherwise, this will just copy the record and all its fields while ignoring 
        records that need to be created and be associated with it.
        Refer to sample copy demo model action for example

        Use set_field_values to have a fix or set value for some fields being copied.
        Format would be:
        {
            "<app_name>.<model_name>.<field_name>": <lambda function(field_value) that returns the fixed_value>,
            ...
        }

        Use cases of set_field_values
        - assign a default value e.g. lambda: False will always make the copied record 
          have a field value of False
        - assign a value that will always be unique

        Returns a list of error messages if any
    """
    # Using a stack data structure to create instances in the proper order. 
    stack: list[ModelCreationData] = []

    # Eliminates possible duplication of ref ids. These ids (uid generated) make it 
    # possible for a child record to store reference of a field it needs to associate 
    # to from a previous instance in the recursion
    fks_ref_id_set: set[str] = set()

    # This will store instances that have been saved already so that succeeding instances 
    # can reference it (such as fk)
    # Format {<uid>: ModelInstanceType}
    created_models: dict = {}

    error_messages: list[str] = []

    # Helper function to recursively apply the same copying of records because some 
    # fields will be instances rather than actual values
    def recursive_copy(instance, recursive_parent_uid="", recursive_parent_instance=None):
        # Get the model of the instance
        instance_app_label = instance._meta.app_label
        instance_model_name = instance._meta.model_name
        instance_model = get_model(f"{instance_app_label}.{instance_model_name}")

        ## Will store the values need for copying the current instance
        # stores each field with a copied value of the instance copy {<field_name>: <value of field>}
        field_values = {}

        # store m2m relationships {<field_name>: [ModelInstanceType,...]}
        m2m_fields = {}

        # the class of the last instance before going to a recursive call e.g. <class "users.models.ChildCustomerType">
        recursive_parent_instance_model_class = recursive_parent_instance.__class__ if recursive_parent_instance else None
        
        # the uid of each record that should be created
        current_recursive_uid = f"{uuid4()}"
        fks_ref_id_set.add(current_recursive_uid)

        # store all the fk associations with the instance from the last recursive call
        fks_to_last_parent_instance: list[dict] = []

        # Go through each fields of the instances
        for field in instance._meta.get_fields():
            try:
                # Get the current value of the field
                is_model_defined_field, field_value = get_model_defined_field_value(
                    field, 
                    instance
                )

                # If the field is not defined in the model of the instance (includes inherited fields),
                # then these are models that are related to the model and need to be created.
                # E.g. If a PageComponent model has another PageComponent under it, then 
                # an instance of that child PageComponent needs to be created.
                if is_model_defined_field:
                    if isinstance(field, models.OneToOneRel):
                        recursive_copy(field_value, current_recursive_uid, instance)
                    
                    # # If the field is a foreign key 
                    # E.g. current instance is PageComponent and has a field named page which is FK to Page
                    elif isinstance(field, models.fields.related.ForeignKey):
                        # Get the model of the foreign key
                        fk_model = field.related_model

                        # If true, it means that you just need to get the instance associated 
                        # with the fk field
                        if fk_model != recursive_parent_instance_model_class:
                            field_values[field.name] = getattr(instance, field.name)
                        else:
                            # This means the fk is the last instance from the last recursion
                            # This will be handled after the recursive copy
                            if recursive_parent_instance:
                                
                                fks_to_last_parent_instance.append({
                                    "field_name": field.name,
                                    "instance_model": recursive_parent_instance_model_class,
                                    "created_model_fk_instance_uid": recursive_parent_uid
                                })
                                field_values[field.name] = None

                    # If the field is defined as a manytomany field in the model
                    # Association is handled after recursive copy
                    elif isinstance(field, models.ManyToManyField):
                        related_instances = list(field_value.all())
                        m2m_fields[field.name] = related_instances

                    # Gets all instances of a model that relates to it through current instance 
                    # as the fk. It means these child records need to be created as well
                    # E.g. Current instance is page and components model relate to it
                    elif isinstance(field, models.ManyToOneRel):
                        for record in field_value.all():
                            recursive_copy(record, current_recursive_uid, instance)

                    # If the field to be copied should have a fixed / set value. 
                    elif set_field_values.get(
                        f"{instance_app_label}.{instance_model_name}.{field.name}"
                    ) is not None:
                        # Invoke the function to generate the fixed value and assign it
                        field_values[field.name] = set_field_values.get(
                            f"{instance_app_label}.{instance_model_name}.{field.name}"
                        )(field_value) 

                        continue

                    else:
                        field_type = field.__class__.__name__

                        if field.unique:
                            # Skip this since this is auto created when model is saved
                            if field.name == "id":
                                continue

                            # Generate the uid in advance if it is a uid field
                            elif field.name == "uid" and has_model_method(instance, "generate_uid"):
                                field_values[field.name] = instance.generate_uid()
                                continue

                            # Seldom cases of unique integer fields that are not auto created
                            elif is_number_type_field(field_type):
                                max_value = instance_model.objects.aggregate(Max(field.name))
                                field_values[field.name] = max_value + 1

                            # Just add a uid to the current value to make it unique
                            else:
                                field_values[field.name] = f"{field_value}-copy-{uuid4()}"

                        # Just means that it is safe to copy the value of the field directly
                        else:
                            field_values[field.name] = field_value
            except Exception as e:
                error_messages.append(f"Error copying {field.name} from {instance_app_label}.{instance_model_name} - {str(e)}\n")

        try:
            model_creation_data = ModelCreationData(
                class_model=instance_model,
                model_ref_uid=current_recursive_uid,
                model_fields=field_values,
                m2m_fields=m2m_fields,
                has_recursive_parent_instance=recursive_parent_instance,
                fks_to_last_parent_instance=fks_to_last_parent_instance
            )

            stack.append(model_creation_data)
        except Exception as e:
            error_messages.append(f"Failed to add to stack {str(model_creation_data.class_model)} - {str(e)}\n")

    recursive_copy(instance)

    while len(stack) > 0:
        model_creation_data = stack.pop()

        # Get the final unique fks based off fks_ref_id_set since it may be possible to have 
        # a duplicate in fks_to_last_parent_instance because of recursion
        final_fks_to_last_parent_instance = []
        for ref_id in fks_ref_id_set:
            for fks in model_creation_data.fks_to_last_parent_instance:
                if fks.get("created_model_fk_instance_uid") == ref_id:
                    final_fks_to_last_parent_instance.append(fks)
                    break

        with transaction.atomic():
            # This is a true when a recursion happens so we need to update the model fields 
            # to associate them with the right fk instance from models that have been created
            if model_creation_data.has_recursive_parent_instance:
                for fks in final_fks_to_last_parent_instance:
                    model_creation_data.model_fields[fks.get("field_name")] = created_models.get(
                        fks.get("created_model_fk_instance_uid")
                    )

            try:
                record = model_creation_data.class_model(**model_creation_data.model_fields)
                created_models[model_creation_data.model_ref_uid] = record
                record.save()

                # Now, we set the m2m relationship after saving the model
                for field_name, related_instances in model_creation_data.m2m_fields.items():
                    getattr(record, field_name).set(related_instances)
            except Exception as e:
                error_messages.append(f"Error creating record for {str(model_creation_data.class_model)} - {str(e)}\n")

    return error_messages