from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomerUser

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'department','is_staff', 'is_active', 'is_superuser', 'is_manager', 'is_dept_head', 'is_citymanager_office','is_global_performance_officer')
    list_filter = ('is_staff', 'is_manager', 'is_active', 'department')
    fieldsets = (
        ('Email and Department', {'fields': ('email', 'password',  'department', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_manager','is_superuser', 'is_dept_head', 'is_citymanager_office')}),
        ('Performance Officer Settings', {'fields': ('is_global_performance_officer', 'accessible_departments')}),
    )
    add_fieldsets = (
        ('Section 2', {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

admin.site.register(CustomerUser, UserAdmin)