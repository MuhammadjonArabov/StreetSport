from django.contrib import admin
from . import models

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone_number', 'full_name', 'role', 'date_joined', 'is_active', 'is_staff')
    exclude = ('password',)
    search_fields = ('full_name', 'phone')
