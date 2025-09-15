from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Add custom fields to the list display in the admin
    list_display = ('username', 'email', 'phone_number', 'user_type', 'is_staff')

    # Add custom fields to the fieldsets for the user creation/editing forms
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'phone_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type', 'phone_number')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
