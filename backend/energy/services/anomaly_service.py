import statistics
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.db.models import Avg, Sum
from ..models import EnergyConsumption, DailyStatistics, AnomalyAlert, SavingRecommendation, AnomalyLog
from ..utils.time_utils import get_current_time
from devices.models import Device, DeviceAction


def _log_anomaly(device, anomaly_type, load_ratio, description):
    AnomalyLog.objects.create(
        device=device,
        anomaly_type=anomaly_type,
        load_ratio=round(load_ratio, 4),
        description=description,
    )


def _update_or_create_alert(device, anomaly_type, severity, description, current_value, expected_value):
    with transaction.atomic():
        Device.objects.select_for_update().get(pk=device.pk)
        existing = AnomalyAlert.objects.filter(
            device=device, anomaly_type=anomaly_type, resolved_at__isnull=True
        ).first()
        if existing:
            existing.severity = severity
            existing.description = description
            existing.current_value = current_value
            existing.expected_value = expected_value
            existing.detected_at = timezone.now()
            existing.resolved_at = None
            existing.save()
            return existing
        return AnomalyAlert.objects.create(
            device=device, anomaly_type=anomaly_type, severity=severity,
            description=description, current_value=current_value,
            expected_value=expected_value,
        )


def run_anomaly_detection():
    alerts = []
    now = get_current_time()
    rated = lambda d: d.rated_power or 1.0

    for device in Device.objects.filter(status='online'):
        last_action = DeviceAction.objects.filter(device=device).first()
        hours_since_toggle = 0
        if last_action:
            hours_since_toggle = (now - last_action.timestamp).total_seconds() / 3600

        last_24h = now - timedelta(hours=24)
        consumption_24h = list(EnergyConsumption.objects.filter(
            device=device, timestamp__gte=last_24h
        ).order_by('timestamp'))

        load_ratio = device.current_power / rated(device) if rated(device) else 0
        power_values = [c.power for c in consumption_24h]

        ctx = {
            'load_ratio': round(load_ratio, 4),
            'hours_since_toggle': round(hours_since_toggle, 2),
            'power_values': power_values,
        }

        if device.power_state == 'on':
            for check in [_check_overload, _check_forgotten, _check_stuck_sensor, _check_erratic]:
                alert = check(device, ctx)
                if alert:
                    alerts.append(alert)
            alert = _check_night_work(device, ctx, now)
            if alert:
                alerts.append(alert)

    return alerts


def _check_overload(device, ctx):
    if ctx['load_ratio'] > 0.9:
        desc = f"{device.name} работает на {(ctx['load_ratio']*100):.0f}% от номинала"
        alert = _update_or_create_alert(
            device, 'overload', 'high', desc,
            ctx['load_ratio'], 0.8,
        )
        _log_anomaly(device, 'overload', ctx['load_ratio'], desc)
        return alert
    return None


def _check_forgotten(device, ctx):
    if device.device_type not in ('climate', 'light', 'other'):
        return None
    if ctx['hours_since_toggle'] > 12:
        desc = f"{device.name} включено более {int(ctx['hours_since_toggle'])}ч без переключения"
        alert = _update_or_create_alert(
            device, 'forgotten', 'medium', desc,
            ctx['hours_since_toggle'], 8,
        )
        _log_anomaly(device, 'forgotten', ctx['load_ratio'], desc)
        return alert
    return None


def _check_night_work(device, ctx, now):
    hour = now.hour
    if hour >= 1 and hour <= 5 and device.power_state == 'on' \
            and device.device_type in ('climate', 'light', 'appliance', 'other', 'Свет'):
        desc = f"{device.name} работает в {hour}ч ночи — возможно, стоит отключить"
        alert = _update_or_create_alert(
            device, 'night_work', 'low', desc, 1, 0,
        )
        _log_anomaly(device, 'night_work', ctx['load_ratio'], desc)
        return alert
    return None


def _check_stuck_sensor(device, ctx):
    now = get_current_time()
    last_6h = now - timedelta(hours=6)
    recent = EnergyConsumption.objects.filter(
        device=device, timestamp__gte=last_6h
    ).values_list('power', flat=True)
    if recent.count() < 6:
        return None
    powers = list(recent)
    if abs(max(powers) - min(powers)) < 0.01 and powers[-1] > 0:
        desc = f"{device.name}: показания не меняются более 6ч — возможна неисправность счётчика"
        alert = _update_or_create_alert(
            device, 'stuck', 'high', desc, powers[-1], 0,
        )
        _log_anomaly(device, 'stuck', ctx['load_ratio'], desc)
        return alert
    return None


def _check_erratic(device, ctx):
    if len(ctx.get('power_values', [])) < 6:
        return None
    powers = ctx['power_values']
    mean_p = statistics.mean(powers)
    if mean_p < 0.01:
        return None
    cv = statistics.stdev(powers) / mean_p if mean_p > 0 else 0
    if cv > 1.2:
        desc = f"{device.name}: хаотичные скачки мощности (CV={cv:.1f})"
        alert = _update_or_create_alert(
            device, 'erratic', 'medium', desc, cv, 0.5,
        )
        _log_anomaly(device, 'erratic', ctx['load_ratio'], desc)
        return alert
    return None


def generate_saving_scenarios():
    now = get_current_time()
    last_7d = now - timedelta(days=7)
    scenarios = []

    for device in Device.objects.filter(status='online'):
        recent_logs = AnomalyLog.objects.filter(
            device=device, created_at__gte=last_7d
        )
        overload_count = recent_logs.filter(anomaly_type='overload').count()
        night_count = recent_logs.filter(anomaly_type='night_work').count()
        forgotten_count = recent_logs.filter(anomaly_type='forgotten').count()

        if overload_count > 0:
            title = f"Проверьте {device.name} на неисправность"
            description = (f"За последние 7 дней зафиксировано {overload_count} случаев перегрузки "
                           f"(>90% от номинала). Рекомендуется проверить устройство на неисправность "
                           f"или перегрев.")
            rec, created = SavingRecommendation.objects.get_or_create(
                device=device, scenario_type='replacement',
                defaults=dict(title=title, description=description,
                              current_cost=0, estimated_savings=0,
                              savings_percent=0),
            )
            if created:
                scenarios.append(rec)

        if night_count > 0:
            title = f"Отключите {device.name} в ночное время"
            description = (f"За последние 7 дней зафиксировано {night_count} случаев работы "
                           f"в ночные часы. Отключение на ночь снизит потребление и продлит "
                           f"срок службы.")
            rec, created = SavingRecommendation.objects.get_or_create(
                device=device, scenario_type='night_shift',
                defaults=dict(title=title, description=description,
                              current_cost=0, estimated_savings=0,
                              savings_percent=0),
            )
            if created:
                scenarios.append(rec)

        if forgotten_count > 0:
            title = f"Настройте расписание для {device.name}"
            description = (f"Устройство было оставлено включённым более 12ч {forgotten_count} раз "
                           f"за последние 7 дней. Автоматическое расписание решит проблему.")
            rec, created = SavingRecommendation.objects.get_or_create(
                device=device, scenario_type='schedule',
                defaults=dict(title=title, description=description,
                              current_cost=0, estimated_savings=0,
                              savings_percent=0),
            )
            if created:
                scenarios.append(rec)

        stats = DailyStatistics.objects.filter(
            device=device, date__gte=last_7d.date()
        )
        total_cost = stats.aggregate(Sum('cost'))['cost__sum'] or 0
        monthly_cost = (total_cost / max(len(stats), 1)) * 30

        if device.device_type in ('climate', 'light', 'other') and monthly_cost > 100 \
                and not SavingRecommendation.objects.filter(
                    device=device, scenario_type='schedule',
                    title__startswith='Настройте расписание').exists():
            rec, created = SavingRecommendation.objects.get_or_create(
                device=device, scenario_type='schedule',
                defaults=dict(
                    title=f'Настроить расписание для {device.name}',
                    description='Отключение на 8ч/день сэкономит до 30%',
                    current_cost=round(monthly_cost, 2),
                    estimated_savings=round(monthly_cost * 0.3, 2),
                    savings_percent=30,
                ),
            )
            if created:
                scenarios.append(rec)

    return list(SavingRecommendation.objects.filter(
        device__status='online'
    ).select_related('device'))
