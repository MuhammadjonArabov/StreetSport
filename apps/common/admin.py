from django.contrib import admin
from .models import Team, Stadium, Bron


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'owner__phone_number')
    filter_horizontal = ('members',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'manager', 'price_hour', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'owner__phone_number', 'manager__phone_number')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


@admin.register(Bron)
class BronAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'stadium', 'start_time', 'end_time', 'is_paid', 'order_type')
    list_filter = ('is_paid', 'order_type', 'start_time')
    search_fields = ('user__phone_number', 'stadium__name', 'team__name')
    date_hierarchy = 'start_time'
    ordering = ('-start_time',)
