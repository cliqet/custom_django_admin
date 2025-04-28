from django.contrib import admin

from django_admin.admin import BaseCustomInline, BaseModelAdmin
from django_admin.constants import DASHBOARD_URL_PREFIX

from .models import Classification, Country, CountryProfile, DemoModel, Level, Type


# It is possible for non-related models to be inlines
class CountryProfileCustomInline(BaseCustomInline):
    app_label = 'demo'
    model_name = 'countryprofile'
    model_name_label = 'CountryProfile'
    list_display = ['country', 'level', 'type', 'area']
    list_display_links = ['country']
    list_per_page = 5
    custom_change_link = f'{DASHBOARD_URL_PREFIX}/custom-change/country-profile'

    def get_queryset(self, change_obj):
        return CountryProfile.objects.all()


# It is possible to have the same model as the inline
class TypeCustomInline(BaseCustomInline):
    app_label = 'demo'
    model_name = 'type'
    model_name_label = 'Type'
    list_display = ['name']
    list_display_links = ['name']
    list_per_page = 5

    # Sample of customizing the queryset of the inline
    def get_queryset(self, change_obj):
        return Type.objects.all()


class DemoModelCustomInline(BaseCustomInline):
    app_label = 'demo'
    model_name = 'demomodel'
    model_name_label = 'DemoModel'
    list_display = ['name', 'type', 'color', 'ordering', 'is_active', 'email']
    list_display_links = ['name']
    list_per_page = 5

    # Using the change_obj to show only those that are related to the change object
    def get_queryset(self, change_obj):
        return DemoModel.objects.filter(type=change_obj)


class TypeAdmin(BaseModelAdmin):
    list_display = ['name']
    list_display_links = ['name']
    search_fields = ['name']
    custom_inlines = [DemoModelCustomInline, TypeCustomInline, CountryProfileCustomInline]
    extra_inlines = ['sample_extra']
    fieldsets = (
        ('Section 1', {
            'fields': ('name',),
        }),
    )


class ClassificationAdmin(BaseModelAdmin):
    list_display = ['id', 'name']
    fieldsets = (
        ('Section 1', {
            'fields': ('name',),
        }),
    )


class DemoModelAdmin(BaseModelAdmin):
    list_display = [
        'name', 'type', 'color', 'ordering', 'is_active', 'email', 'date', 'metadata', 'html'
    ]
    ordering = ['-name', 'type']
    search_fields = ['name', 'email']
    search_help_text = 'Search by name, email'
    autocomplete_fields = ['type']
    list_filter = ['color', 'type', 'is_active']
    list_per_page = 5
    fieldsets = (
        ('Section 1', {
            'fields': (
                'type', 'color', 'name', 'email', 'ordering', 'range_number',
                'amount', 'comment', 'is_active'
            ),
        }),
        ('Section 2', {
            'fields': (
                'date', 'time', 'last_log', 'classification', 'permissions',
                'file', 'image', 'metadata', 'html'
            ),
        }),
    )


class LevelAdmin(BaseModelAdmin):
    ...


class CountryAdmin(BaseModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    search_help_text = ['Search by name']


class CountryProfileAdmin(BaseModelAdmin):
    list_display = ['country', 'level', 'type', 'area']
    autocomplete_fields = ['country']
    custom_change_link = f'{DASHBOARD_URL_PREFIX}/custom-change/country-profile'

admin.site.register(Type, TypeAdmin)
admin.site.register(Classification, ClassificationAdmin)
admin.site.register(DemoModel, DemoModelAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(CountryProfile, CountryProfileAdmin)
