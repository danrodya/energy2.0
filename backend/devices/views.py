from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import IntegrityError
import random

from .models import Device, DeviceAction, Schedule, PresetSchedule, PresetScheduleEntry
from .serializers import DeviceSerializer, ScheduleSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all().prefetch_related('errors', 'actions', 'schedules')
    serializer_class = DeviceSerializer

    def destroy(self, request, *args, **kwargs):
        from django.http import HttpResponse
        from django.db import connection
        try:
            instance = self.get_object()
            device_id = instance.id
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM devices_anomalyalert WHERE device_id = %s", [device_id])
                cursor.execute("DELETE FROM energy_anomalyalert WHERE device_id = %s", [device_id])
                cursor.execute("DELETE FROM energy_anomalylog WHERE device_id = %s", [device_id])
                cursor.execute("DELETE FROM energy_savingrecommendation WHERE device_id = %s", [device_id])
                cursor.execute("DELETE FROM energy_energyconsumption WHERE device_id = %s", [device_id])
                cursor.execute("DELETE FROM energy_dailystatistics WHERE device_id = %s", [device_id])
                cursor.execute("DELETE FROM devices_deviceaction WHERE device_id = %s", [device_id])
                cursor.execute("DELETE FROM devices_deviceerror WHERE device_id = %s", [device_id])
                cursor.execute("DELETE FROM devices_schedule WHERE device_id = %s", [device_id])
                cursor.execute("DELETE FROM devices_device WHERE id = %s", [device_id])
            return HttpResponse(status=204)
        except Exception as e:
            import traceback
            return HttpResponse(f'ERROR: {e}\n{traceback.format_exc()}', status=500, content_type='text/plain')
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Включить/выключить устройство"""
        device = self.get_object()
        device.power_state = 'off' if device.power_state == 'on' else 'on'
        if device.power_state == 'on':
            if random.random() < 0.35:
                device.current_power = round(random.uniform(
                    device.rated_power * 0.91,
                    device.rated_power * 1.0
                ), 4)
            else:
                device.current_power = round(random.uniform(
                    device.rated_power * 0.1,
                    device.rated_power * 0.7
                ), 4)
        else:
            device.current_power = 0
        device.save()
        
        DeviceAction.objects.create(
            device=device,
            action_type='toggle',
            details={'new_state': device.power_state, 'power': device.current_power}
        )
        
        return Response({
            'status': 'device toggled',
            'device': DeviceSerializer(device).data
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Сводка по всем устройствам"""
        devices = Device.objects.all()
        total_power = sum(d.current_power for d in devices)
        online_count = devices.filter(status='online').count()
        
        return Response({
            'total_devices': devices.count(),
            'online_devices': online_count,
            'offline_devices': devices.count() - online_count,
            'total_current_power': round(total_power, 2),
            'devices': DeviceSerializer(devices, many=True).data
        })
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """История действий устройства"""
        device = self.get_object()
        actions = device.actions.all().order_by('-timestamp')
        return Response([{
            'timestamp': a.timestamp,
            'action': a.action_type,
            'details': a.details
        } for a in actions])
    
    @action(detail=True, methods=['get'])
    def errors(self, request, pk=None):
        """Ошибки и предупреждения устройства"""
        device = self.get_object()
        errors_qs = device.errors.all().order_by('-created_at')
        return Response([{
            'id': e.id,
            'title': e.error_type,
            'description': e.description,
            'severity': e.severity,
            'date': e.created_at,
            'resolved_at': e.resolved_at,
        } for e in errors_qs])

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        qs = Schedule.objects.all()
        device_id = self.request.query_params.get('device_id')
        status = self.request.query_params.get('status')
        if device_id:
            qs = qs.filter(device_id=device_id)
        if status:
            qs = qs.filter(enabled=(status == 'active'))
        return qs.order_by('time')
    
    @action(detail=False, methods=['get'])
    def by_device(self, request):
        """Получить все расписания для устройства"""
        device_id = request.query_params.get('device_id')
        if not device_id:
            return Response({'error': 'device_id required'}, status=400)
        
        schedules = Schedule.objects.filter(device_id=device_id).order_by('time')
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_for_device(self, request):
        """Создать расписание для устройства"""
        device_id = request.data.get('device_id')
        time = request.data.get('time')
        action = request.data.get('action')
        
        if not all([device_id, time, action]):
            return Response({'error': 'Missing required fields'}, status=400)
        
        schedule = Schedule.objects.create(
            device_id=device_id,
            time=time,
            action=action,
            enabled=True
        )
        serializer = self.get_serializer(schedule)
        return Response(serializer.data, status=201)
    
    @action(detail=True, methods=['patch'])
    def toggle_enabled(self, request, pk=None):
        """Включить/отключить расписание"""
        schedule = self.get_object()
        schedule.enabled = not schedule.enabled
        schedule.save()
        
        serializer = self.get_serializer(schedule)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Активировать расписание"""
        schedule = self.get_object()
        schedule.enabled = True
        schedule.save()
        serializer = self.get_serializer(schedule)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Деактивировать расписание"""
        schedule = self.get_object()
        schedule.enabled = False
        schedule.save()
        serializer = self.get_serializer(schedule)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """История выполнения расписания"""
        schedule = self.get_object()
        actions = DeviceAction.objects.filter(
            device=schedule.device,
            action_type__in=['schedule_on', 'schedule_off']
        ).order_by('-timestamp')[:int(request.query_params.get('days', 30))]
        return Response([{
            'timestamp': a.timestamp,
            'action': a.action_type,
            'details': a.details
        } for a in actions])
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Список шаблонов расписаний"""
        device_type = request.query_params.get('device_type')
        qs = PresetSchedule.objects.all()
        if device_type:
            qs = qs.filter(recommended_for__icontains=device_type)
        return Response([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'category': p.category,
            'icon': p.icon,
            'estimated_savings': p.estimated_savings,
            'recommended_for': p.recommended_for,
            'entries': [{
                'day_of_week': e.day_of_week,
                'start_time': str(e.start_time),
                'end_time': str(e.end_time),
                'action': e.action
            } for e in p.entries.all()]
        } for p in qs])
    
    @action(detail=False, methods=['post'])
    def from_template(self, request):
        """Создать расписание из шаблона"""
        template_id = request.data.get('template_id')
        device_id = request.data.get('device_id')
        if not all([template_id, device_id]):
            return Response({'error': 'template_id and device_id required'}, status=400)
        try:
            preset = PresetSchedule.objects.get(id=template_id)
        except PresetSchedule.DoesNotExist:
            return Response({'error': 'template not found'}, status=404)
        entries = preset.entries.all()
        created = []
        for entry in entries:
            schedule = Schedule.objects.create(
                device_id=device_id,
                time=entry.start_time,
                action=entry.action,
                enabled=True
            )
            created.append(schedule)
        return Response({
            'created': len(created),
            'schedules': ScheduleSerializer(created, many=True).data
        }, status=201)