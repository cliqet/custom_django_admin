from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group
from django.contrib.sessions.models import Session
from rest_framework import serializers
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)


class BaseModelSerializer(serializers.ModelSerializer):
    """
        Use for all ModelSerializer implementations since it formats related models
        in a way where it will have the pk and a string representation instead of just
        the pk
    """
    pk = serializers.SerializerMethodField()

    def get_pk(self, obj):
        return obj.pk
    
    def to_representation(self, instance):
        # Call the parent implementation to get the default representation
        representation = super().to_representation(instance)

        for field, value in representation.items():
            # Check if the field is a related model
            if isinstance(value, list): 
                # Get actual model instances
                all_objects = getattr(instance, field).all()
                
                representation[field] = [
                    {
                        'pk': related_obj.pk,
                        'string_value': related_obj.__str__(),
                    } 
                    for related_obj in all_objects
                ]
            else:
                representation[field] = value
        return representation


# Serializer for individual models in the app
class ModelPermSerializer(serializers.Serializer):
    add = serializers.BooleanField()
    change = serializers.BooleanField()
    delete = serializers.BooleanField()
    view = serializers.BooleanField()


class AppModelSerializer(serializers.Serializer):
    name = serializers.CharField()
    object_name = serializers.CharField()
    admin_url = serializers.CharField()
    add_url = serializers.CharField(allow_blank=True)
    perms = ModelPermSerializer()
    view_only = serializers.BooleanField()

# Serializer for the app
class AppSerializer(serializers.Serializer):
    name = serializers.CharField()
    app_label = serializers.CharField()
    app_url = serializers.CharField()
    has_module_perms = serializers.BooleanField()
    models = serializers.ListField(child=AppModelSerializer())


class ContentTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    app_label = serializers.CharField()
    model = serializers.CharField()


class PermissionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    codename = serializers.CharField()
    content_type = ContentTypeSerializer()


class GroupSerializer(BaseModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class LogEntrySerializer(BaseModelSerializer):
    class Meta:
        model = LogEntry
        fields = '__all__'


class SessionSerializer(BaseModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


# 3rd party apps =================================================================
class BlacklistedTokenSerializer(BaseModelSerializer):
    class Meta:
        model = BlacklistedToken
        fields = '__all__'


class OutstandingTokenSerializer(BaseModelSerializer):
    class Meta:
        model = OutstandingToken
        fields = '__all__'

# =================================================================

class ForeignKeyChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()  # Accepts both numbers and strings
    label = serializers.CharField()
    selected = serializers.BooleanField()


class ManyToManyChoiceSerializer(serializers.Serializer):
    id = serializers.CharField()  # Accepts both numbers and strings
    label = serializers.CharField()
    checked = serializers.BooleanField()


class FieldAttributeChoiceSerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.JSONField()  # Any value depending on the field type
    selected = serializers.BooleanField()


class FieldAttributeSerializer(serializers.Serializer):
    name = serializers.CharField()
    label = serializers.CharField()
    is_primary_key = serializers.BooleanField()
    max_length = serializers.IntegerField(required=False, allow_null=True)
    editable = serializers.BooleanField()
    help_text = serializers.CharField(allow_blank=True)
    auto_created = serializers.BooleanField()
    type = serializers.CharField()
    initial = serializers.CharField(allow_null=True)
    required = serializers.BooleanField()
    choices = serializers.ListField(child=FieldAttributeChoiceSerializer(), required=False, allow_null=True)
    min_value = serializers.IntegerField(allow_null=True)
    max_value = serializers.IntegerField(allow_null=True)

    decimal_places = serializers.IntegerField(required=False)
    max_digits = serializers.IntegerField(required=False)
    regex_pattern = serializers.CharField(required=False)
    regex_message = serializers.CharField(required=False)
    foreignkey_choices = serializers.ListField(
        child=ForeignKeyChoiceSerializer(), required=False, allow_null=True
    )
    foreignkey_model = serializers.CharField(required=False, allow_blank=True)
    foreignkey_app = serializers.CharField(required=False, allow_blank=True)
    
    manytomany_choices = serializers.ListField(
        child=ManyToManyChoiceSerializer(), required=False, allow_null=True
    )
    manytomany_related_app = serializers.CharField(required=False, allow_blank=True)
    manytomany_related_model = serializers.CharField(required=False, allow_blank=True)


class ModelFieldSerializer(serializers.Serializer):
    fields = serializers.DictField(child=FieldAttributeSerializer())


class FieldsetSerializer(serializers.Serializer):
    title = serializers.CharField()
    fields = serializers.ListField(child=serializers.CharField())


class CustomActionSerializer(serializers.Serializer):
    func = serializers.CharField()
    label = serializers.CharField()


class CustomInlineSerializer(serializers.Serializer):
    app_label = serializers.CharField()
    model_name = serializers.CharField()
    model_name_label = serializers.CharField()
    list_display = serializers.ListField(child=serializers.CharField())
    list_display_links = serializers.ListField(child=serializers.CharField())
    custom_change_link = serializers.CharField()
    list_per_page = serializers.IntegerField()
    class_name = serializers.SerializerMethodField()

    def get_class_name(self, obj):
        # Return the class name of the current instance
        return obj.__name__


class TableFilterValueSerializer(serializers.Serializer):
    value = serializers.CharField(allow_null=True)
    label = serializers.CharField()


class TableFilterSerializer(serializers.Serializer):
    field = serializers.CharField()
    values = serializers.ListField(child=TableFilterValueSerializer())


class ModelAdminSettingsSerializer(serializers.Serializer):
    model_name = serializers.CharField()
    app_label = serializers.CharField()
    fieldsets = FieldsetSerializer()
    list_display = serializers.ListField(child=serializers.CharField())
    list_per_page = serializers.IntegerField()
    list_display_links = serializers.ListField(child=serializers.CharField())
    search_fields = serializers.ListField(child=serializers.CharField())
    search_help_text = serializers.CharField()
    ordering = serializers.ListField(child=serializers.CharField())
    autocomplete_fields = serializers.ListField(child=serializers.CharField())
    readonly_fields = serializers.ListField(child=serializers.CharField())
    custom_actions = serializers.ListField(child=CustomActionSerializer())
    custom_inlines = serializers.ListField(child=CustomInlineSerializer())
    table_filters = serializers.ListField(child=TableFilterSerializer())
    extra_inlines = serializers.ListField(child=serializers.CharField())
    custom_change_link = serializers.CharField()


class VerifyTokenBodySerializer(serializers.Serializer):
    token = serializers.CharField()

