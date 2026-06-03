from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Avg, Max, Min
from datetime import timedelta, date
import random
from .models import EnergyConsumption, DailyStatistics, AnomalyAlert, SavingRecommendation, TimeOverride
from .serializers import (EnergyConsumptionSerializer, DailyStatisticsSerializer,
                          AnomalyAlertSerializer, SavingRecommendationSerializer, TimeOverrideSerializer)
from .services.anomaly_service import run_anomaly_detection, generate_saving_scenarios
from .utils.time_utils import get_current_time, set_simulated_time, clear_simulated_time
from devices.models import Device


class EnergyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EnergyConsumption.objects.all()
    serializer_class = EnergyConsumptionSerializer

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Текущее потребление всех устройств"""
        today = timezone.now().date()
        devices = Device.objects.all()

        data = []
        for device in devices:
            daily = DailyStatistics.objects.filter(device=device, date=today).first()
            data.append({
                'id': device.id,
                'name': device.name,
                'device_type': device.device_type,
                'current_power': device.current_power,
                'rated_power': device.rated_power,
                'last_update': device.last_update,
                'daily_consumption': daily.total_energy if daily else 0,
                'status': device.status,
                'power_state': device.power_state,
            })

        total_power = sum(d['current_power'] for d in data)

        return Response({
            'timestamp': timezone.now(),
            'total_power': round(total_power, 2),
            'devices': data
        })

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Потребление за текущий день"""
        today = timezone.now().date()
        stats = DailyStatistics.objects.filter(date=today)

        total_energy = stats.aggregate(Sum('total_energy'))['total_energy__sum'] or 0
        total_cost = stats.aggregate(Sum('cost'))['cost__sum'] or 0

        return Response({
            'date': today,
            'total_energy': round(total_energy, 2),
            'total_cost': round(total_cost, 2),
            'devices': DailyStatisticsSerializer(stats, many=True).data
        })

    @action(detail=False, methods=['get'])
    def hourly(self, request):
        """Почасовые данные"""
        date_str = request.query_params.get('date')
        target_date = timezone.now().date() if not date_str else timezone.datetime.strptime(date_str, '%Y-%m-%d').date()

        consumptions = EnergyConsumption.objects.filter(
            timestamp__date=target_date
        ).order_by('timestamp')

        hourly_data = []
        for hour in range(24):
            start = timezone.make_aware(timezone.datetime.combine(target_date, timezone.datetime.min.time())) + timedelta(hours=hour)
            end = start + timedelta(hours=1)

            hour_consumptions = consumptions.filter(timestamp__gte=start, timestamp__lt=end)
            power = hour_consumptions.aggregate(Avg('power'))['power__avg'] or random.uniform(2, 8)

            hourly_data.append({
                'time': f"{hour:02d}:00",
                'power': round(power, 2),
                'energy': round(power * 1.0, 2)
            })

        return Response(hourly_data)

    @action(detail=False, methods=['get'])
    def daily(self, request):
        """Суточные данные за месяц"""
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))

        from datetime import date as date_class
        first_day = date_class(year, month, 1)
        if month == 12:
            last_day = date_class(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date_class(year, month + 1, 1) - timedelta(days=1)

        stats = DailyStatistics.objects.filter(
            date__gte=first_day,
            date__lte=last_day
        ).order_by('date')

        data = []
        current = first_day
        while current <= last_day:
            day_stats = stats.filter(date=current)
            total = day_stats.aggregate(Sum('total_energy'))['total_energy__sum'] or 0
            avg = day_stats.aggregate(Avg('avg_power'))['avg_power__avg'] or 0
            peak = day_stats.aggregate(Max('peak_power'))['peak_power__max'] or 0
            cost = day_stats.aggregate(Sum('cost'))['cost__sum'] or 0

            data.append({
                'date': str(current),
                'total_energy': round(total, 2),
                'avg_power': round(avg, 2),
                'peak_power': round(peak, 2),
                'cost': round(cost, 2)
            })
            current += timedelta(days=1)

        return Response(data)

    @action(detail=False, methods=['get'])
    def monthly(self, request):
        """Месячные данные за год"""
        year = int(request.query_params.get('year', timezone.now().year))

        from datetime import date as date_class
        data = []
        month_names = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн',
                       'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дец']

        for month in range(1, 13):
            first_day = date_class(year, month, 1)
            if month == 12:
                last_day = date_class(year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = date_class(year, month + 1, 1) - timedelta(days=1)

            stats = DailyStatistics.objects.filter(
                date__gte=first_day,
                date__lte=last_day
            )

            total = stats.aggregate(Sum('total_energy'))['total_energy__sum'] or 0
            cost = stats.aggregate(Sum('cost'))['cost__sum'] or 0
            avg_power = stats.aggregate(Avg('avg_power'))['avg_power__avg'] or 0
            peak = stats.aggregate(Max('peak_power'))['peak_power__max'] or 0

            data.append({
                'date': month_names[month - 1],
                'month': month,
                'total_energy': round(total, 2),
                'avg_power': round(avg_power, 2),
                'peak_power': round(peak, 2),
                'cost': round(cost, 2)
            })

        return Response(data)

    @action(detail=False, methods=['get'])
    def top_consumers(self, request):
        """Топ потребителей"""
        today = timezone.now().date()
        stats = DailyStatistics.objects.filter(date=today).order_by('-total_energy')[:5]

        data = [
            {
                'name': s.device.name,
                'power': round(s.avg_power, 2)
            }
            for s in stats
        ]

        return Response(data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Общая статистика"""
        today = timezone.now().date()
        stats = DailyStatistics.objects.filter(date=today)

        consumption_data = stats.aggregate(
            total=Sum('total_energy'),
            avg=Avg('avg_power'),
            peak=Max('peak_power'),
            min=Min('peak_power')
        )

        cost = stats.aggregate(Sum('cost'))['cost__sum'] or 0

        return Response({
            'date': today,
            'total_energy': round(consumption_data['total'] or 0, 2),
            'avg_power': round(consumption_data['avg'] or 0, 2),
            'peak_power': round(consumption_data['peak'] or 0, 2),
            'min_power': round(consumption_data['min'] or 0, 2),
            'total_cost': round(cost, 2),
            'devices_count': DailyStatistics.objects.filter(date=today).count()
        })

    @action(detail=False, methods=['get'])
    def forecast(self, request):
        """Прогноз затрат на следующий месяц"""
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        recent_stats = DailyStatistics.objects.filter(date__gte=thirty_days_ago)

        avg_daily = recent_stats.aggregate(Avg('total_energy'))['total_energy__avg'] or 0
        avg_cost_daily = recent_stats.aggregate(Avg('cost'))['cost__avg'] or 0

        forecast_energy = round(avg_daily * 30, 2)
        forecast_cost = round(avg_cost_daily * 30, 2)

        return Response({
            'next_month_energy': forecast_energy,
            'next_month_cost': forecast_cost,
            'daily_average': round(avg_daily, 2),
            'confidence': 82
        })

    @action(detail=False, methods=['get'])
    def comparison(self, request):
        """Сравнение потребления за период"""
        period = request.query_params.get('period', 'week')
        today = timezone.now().date()

        if period == 'week':
            days = 7
        elif period == 'month':
            days = 30
        else:
            days = 1

        current = DailyStatistics.objects.filter(
            date__gte=today - timedelta(days=days)
        ).aggregate(
            total=Sum('total_energy'), avg=Avg('avg_power'), peak=Max('peak_power')
        )
        previous = DailyStatistics.objects.filter(
            date__gte=today - timedelta(days=days * 2),
            date__lt=today - timedelta(days=days)
        ).aggregate(
            total=Sum('total_energy'), avg=Avg('avg_power'), peak=Max('peak_power')
        )

        return Response({
            'period': period,
            'current': {
                'total_energy': round(current['total'] or 0, 2),
                'avg_power': round(current['avg'] or 0, 2),
                'peak_power': round(current['peak'] or 0, 2)
            },
            'previous': {
                'total_energy': round(previous['total'] or 0, 2),
                'avg_power': round(previous['avg'] or 0, 2),
                'peak_power': round(previous['peak'] or 0, 2)
            }
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Экспорт данных"""
        format_type = request.query_params.get('format', 'csv')
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)

        stats = DailyStatistics.objects.filter(
            date__gte=thirty_days_ago
        ).order_by('date')

        data = []
        for stat in stats:
            data.append({
                'date': str(stat.date),
                'device': stat.device.name,
                'energy': stat.total_energy,
                'cost': stat.cost,
                'avg_power': stat.avg_power
            })

        return Response({
            'format': format_type,
            'records': len(data),
            'data': data
        })

    @action(detail=False, methods=['get'])
    def anomalies(self, request):
        """Список аномалий"""
        resolved = request.query_params.get('resolved', 'false').lower() == 'true'
        qs = AnomalyAlert.objects.all()
        if not resolved:
            qs = qs.filter(resolved_at__isnull=True)
        qs = qs.select_related('device').order_by('-severity', '-detected_at')
        return Response(AnomalyAlertSerializer(qs, many=True).data)

    @action(detail=False, methods=['post'])
    def detect_anomalies(self, request):
        """Запустить детекцию аномалий"""
        alerts = run_anomaly_detection()
        return Response({
            'detected': len(alerts),
            'anomalies': AnomalyAlertSerializer(alerts, many=True).data
        })

    @action(detail=False, methods=['get'])
    def saving_scenarios(self, request):
        """Сценарии экономии"""
        implemented = request.query_params.get('implemented', 'false').lower() == 'true'
        qs = SavingRecommendation.objects.select_related('device').all()
        if not implemented:
            qs = qs.filter(implemented=False)
        return Response(SavingRecommendationSerializer(qs, many=True).data)

    @action(detail=False, methods=['post'])
    def generate_scenarios(self, request):
        """Сгенерировать сценарии экономии"""
        scenarios = generate_saving_scenarios()
        return Response({
            'generated': len(scenarios),
            'scenarios': SavingRecommendationSerializer(scenarios, many=True).data
        })

    @action(detail=False, methods=['get'])
    def time(self, request):
        """Получить текущее (возможно симулированное) время"""
        now = get_current_time()
        override = TimeOverride.objects.first()
        return Response({
            'current_time': now,
            'simulated_time': override.simulated_time if override else None,
            'is_overridden': override is not None,
        })

    @action(detail=False, methods=['post'])
    def set_time(self, request):
        """Установить симулированное время"""
        dt_str = request.data.get('simulated_time')
        if not dt_str:
            return Response({'error': 'simulated_time required'}, status=400)
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(dt_str)
        except ValueError:
            return Response({'error': 'invalid datetime format'}, status=400)
        dt = timezone.make_aware(dt) if timezone.is_naive(dt) else dt
        set_simulated_time(dt)
        return Response({
            'simulated_time': timezone.localtime(dt),
            'is_overridden': True,
        })

    @action(detail=False, methods=['post'])
    def clear_time(self, request):
        """Сбросить симулированное время — использовать системное"""
        clear_simulated_time()
        return Response({
            'current_time': timezone.now(),
            'is_overridden': False,
        })

    @action(detail=False, methods=['post'])
    def resolve_anomaly(self, request):
        """Закрыть аномалию"""
        anomaly_id = request.data.get('anomaly_id')
        if not anomaly_id:
            return Response({'error': 'anomaly_id required'}, status=400)
        try:
            alert = AnomalyAlert.objects.get(id=anomaly_id)
            alert.resolved_at = timezone.now()
            alert.save()
            return Response(AnomalyAlertSerializer(alert).data)
        except AnomalyAlert.DoesNotExist:
            return Response({'error': 'not found'}, status=404)
