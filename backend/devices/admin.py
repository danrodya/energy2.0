from django.contrib import admin
from .models import Device, DeviceError, DeviceAction, Schedule


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_type', 'status', 'power_state', 'current_power', 'last_update']
    list_filter = ['status', 'power_state', 'device_type']
    search_fields = ['name', 'description']
    readonly_fields = ['last_update', 'created_at']


@admin.register(DeviceError)
class DeviceErrorAdmin(admin.ModelAdmin):
    list_display = ['device', 'error_type', 'severity', 'created_at', 'resolved_at']
    list_filter = ['severity', 'created_at', 'device']
    search_fields = ['device__name', 'error_type']


@admin.register(DeviceAction)
class DeviceActionAdmin(admin.ModelAdmin):
    list_display = ['device', 'action_type', 'timestamp']
    list_filter = ['action_type', 'timestamp', 'device']
    search_fields = ['device__name']
    readonly_fields = ['timestamp']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['device', 'time', 'action', 'enabled', 'created_at']
    list_filter = ['enabled', 'action', 'created_at']
    search_fields = ['device__name']
    readonly_fields = ['created_at', 'updated_at']