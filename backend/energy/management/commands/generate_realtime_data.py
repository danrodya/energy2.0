from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
import time
import math
from devices.models import Device, DeviceAction, Schedule
from energy.models import EnergyConsumption, DailyStatistics
from energy.services.anomaly_service import run_anomaly_detection


class Command(BaseCommand):
    help = 'Генерирует данные в реальном времени с аномалиями'

    def add_arguments(self, parser):
        parser.add_argument('--duration', type=int, default=3600,
                            help='Длительность в секундах (по умолчанию 1 час)')

    def handle(self, *args, **options):
        duration = options['duration']
        start_time = time.time()
        counter = 0
        anomaly_states = {}

        now = timezone.now()
        today = now.date()
        first_run_today = today

        # Создаём DeviceAction в прошлом, чтобы hours_since_toggle работал
        for device in Device.objects.all():
            DeviceAction.objects.get_or_create(
                device=device,
                action_type='init',
                defaults={
                    'details': {'note': 'initial state'},
                    'timestamp': now - timedelta(hours=16),
                }
            )
            anomaly_states[device.id] = {
                'mode': 'normal',
                'until': now,
                'prev_power': device.current_power,
            }

        self.stdout.write(self.style.SUCCESS(f'Начал генерацию на {duration} секунд...'))

        while time.time() - start_time < duration:
            counter += 1
            now = timezone.now()
            today = now.date()
            hour = now.hour

            devices = Device.objects.all()

            for device in devices:
                state = anomaly_states.get(device.id, {
                    'mode': 'normal', 'until': now, 'prev_power': 0
                })

                # Если устройство выключено пользователем (через UI) — уважаем его выбор
                user_state = Device.objects.get(id=device.id).power_state
                if user_state == 'off':
                    if device.power_state != 'off':
                        device.power_state = 'off'
                        device.current_power = 0
                        device.last_update = now
                        device.save()
                    power = 0
                else:
                    # Переключаем режим аномалии раз в ~2 минуты
                    if now > state['until']:
                        roll = random.random()
                        if roll < 0.15:
                            state['mode'] = random.choice(['overload', 'spike', 'night_work', 'erratic'])
                            duration_sec = random.randint(60, 180)
                            state['until'] = now + timedelta(seconds=duration_sec)
                        else:
                            state['mode'] = 'normal'
                            state['until'] = now + timedelta(seconds=random.randint(120, 600))

                    # Генерируем мощность по режиму
                    if device.status != 'online':
                        power = 0
                    elif state['mode'] == 'normal':
                        if hour >= 23 or hour <= 6:
                            power = random.uniform(0, device.rated_power * 0.2)
                        else:
                            power = random.uniform(device.rated_power * 0.2, device.rated_power * 0.7)
                    elif state['mode'] == 'overload':
                        power = random.uniform(device.rated_power * 0.92, device.rated_power * 1.0)
                    elif state['mode'] == 'spike':
                        base = random.uniform(0, device.rated_power * 0.1)
                        spike = random.uniform(device.rated_power * 0.7, device.rated_power * 0.95)
                        power = max(base, spike) if random.random() < 0.5 else base
                    elif state['mode'] == 'night_work':
                        power = random.uniform(device.rated_power * 0.3, device.rated_power * 0.8)
                    elif state['mode'] == 'erratic':
                        if random.random() < 0.4:
                            power = random.uniform(device.rated_power * 0.8, device.rated_power * 1.0)
                        else:
                            power = random.uniform(0, device.rated_power * 0.05)
                    else:
                        power = 0

                    device.current_power = round(power, 4)
                    device.power_state = 'on' if power > 0.01 else 'off'
                    device.last_update = now
                    device.save()

                # Создаём запись потребления
                EnergyConsumption.objects.create(
                    device=device,
                    power=power,
                    energy=round(power / 12, 6),
                )

            # Обновляем суточную статистику каждые 30 секунд
            if counter % 6 == 0:
                for device in devices:
                    day_consumptions = EnergyConsumption.objects.filter(
                        device=device,
                        timestamp__date=today,
                    )
                    if not day_consumptions.exists():
                        continue

                    total_energy = sum(e.energy for e in day_consumptions)
                    powers = [e.power for e in day_consumptions]
                    avg_power = sum(powers) / len(powers) if powers else 0
                    peak_power = max(powers) if powers else 0
                    cost = total_energy * 7.22

                    DailyStatistics.objects.update_or_create(
                        device=device,
                        date=today,
                        defaults={
                            'total_energy': round(total_energy, 4),
                            'avg_power': round(avg_power, 4),
                            'peak_power': round(peak_power, 4),
                            'cost': round(cost, 2),
                        }
                    )

            # Детекция аномалий каждые 30 секунд
            if counter % 6 == 0:
                detected = run_anomaly_detection()
                active_anomalies = sum(
                    1 for s in anomaly_states.values()
                    if s.get('mode') != 'normal' and now < s.get('until', now)
                )
                self.stdout.write(
                    f'{counter * 5}c | '
                    f'режим аномалий: {active_anomalies} | '
                    f'детектировано: {len(detected)}'
                )

            time.sleep(5)

        self.stdout.write(self.style.SUCCESS('Генерация завершена!'))
