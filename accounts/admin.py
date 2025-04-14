from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Extend the existing fieldsets to include our custom fields.
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("role", "restaurant", "restaurants")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("role", "restaurant", "restaurants")}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
