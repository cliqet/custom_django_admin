from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from django_admin.admin import BaseModelAdmin

from .models import CustomUser


class CustomUserAdmin(BaseUserAdmin, BaseModelAdmin):
    readonly_fields = BaseModelAdmin.readonly_fields + ['uid']
    list_filter = []
    list_display = ['uid', 'email']
    search_fields = []
    search_help_text = 'Search by'
    ordering = []
    filter_horizontal = ['groups']

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email'),
        }),
        ('Security', {
            'fields': ('password',),
        }),
        ('User Settings', {
            'fields': (
                'uid', 'is_active', 'is_staff', 'is_superuser',
                'groups', 'created_at', 'updated_at'
            ),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = (
        ('User Credentials', {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)
