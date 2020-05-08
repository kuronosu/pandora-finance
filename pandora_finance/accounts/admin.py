from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.
class MyUserAdmin(UserAdmin):
    model = User
    fieldsets = [
        ("General", {"fields": [
            'document',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'is_active',
            'password',
            'phone_number',
            'user_type',
            'is_superuser'
        ]}),
        # ("Details", {"fields": ["description", "creation_date"], "classes": ["collapse"]})
    ]
    ordering = ('document',)
    list_display = ('document',)

admin.site.register(User, MyUserAdmin)