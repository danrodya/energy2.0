from rest_framework import serializers
from .models import Device, DeviceError, DeviceAction, Schedule


class DeviceErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceError
        fields = ['id', 'error_type', 'description', 'severity', 'created_at', 'resolved_at']


class DeviceActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceAction
        fields = ['id', 'action_type', 'details', 'timestamp']


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'device', 'time', 'action', 'enabled', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class DeviceSerializer(serializers.ModelSerializer):
    errors = DeviceErrorSerializer(many=True, read_only=True)
    actions = DeviceActionSerializer(many=True, read_only=True)
    schedules = ScheduleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Device
        fields = ['id', 'name', 'device_type', 'status', 'power_state',
                  'current_power', 'rated_power', 'last_update', 'created_at', 
                  'errors', 'actions', 'schedules']
        read_only_fields = ['last_update', 'created_at']