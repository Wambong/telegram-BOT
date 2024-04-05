# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'is_staff', 'is_active']
    ordering = ['email']

admin.site.register(CustomUser, CustomUserAdmin)
