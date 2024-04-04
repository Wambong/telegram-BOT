from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    # Define how you want to display CustomUser objects in the admin panel
    list_display = ['email', 'is_staff', 'is_active']

admin.site.register(CustomUser, CustomUserAdmin)