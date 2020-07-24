from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class MyUserAdmin(UserAdmin):
    model = User
    fieldsets = (
        ("Información personal", {"fields": [
            'document',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'password',
        ]}),
        ('Estados',  {'fields': ['is_staff', 'can_approve',
                                 'is_active', 'is_superuser', 'user_type']}),
        ("Detalles", {"fields": ["date_joined"], "classes": ["collapse"]}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'document',
                'email',
                'first_name',
                'last_name',
                'is_staff',
                'password',
                'phone_number',
                'user_type',
                'is_superuser', 'password1', 'password2'),
        }),
    )
    ordering = ('document',)
    list_display = ('document', 'id', 'email')


admin.site.register(User, MyUserAdmin)
