from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm


class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('uuid', 'username', 'phone_number', 'email', 'is_active', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role', 'uuid')

    fieldsets = (
        (None, {'fields': ('username', 'phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name',  'email', 'photo')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Additional', {'fields': ('role', 'level', 'course', 'direction', 'coins', 'tg_username', 'uuid', 'image_qrkod')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'username', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('last_login', 'created_at', 'updated_at')

    search_fields = ('phone_number', 'username', 'email', 'uuid')
    ordering = ('phone_number',)
    filter_horizontal = ('groups', 'user_permissions')


admin.site.register(User, UserAdmin)