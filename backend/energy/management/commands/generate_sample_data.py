from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from devices.models import Device, DeviceError, DeviceAction
from energy.models import EnergyConsumption, DailyStatistics


class Command(BaseCommand):
    help = 'Генерирует примеры данных для демонстрации'

    def handle(self, *args, **options):
        # Проверяем, есть ли уже устройства
        if Device.objects.exists():
            self.stdout.write(self.style.WARNING('Устройства уже существуют. Пропускаю создание.'))
            return

        # Создаем устройства
        devices_data = [
            ('Кондиционер', 'Климат', 3.5),
            ('Холодильник', 'Кухня', 0.8),
            ('Стиральная машина', 'Бытовая', 2.2),
            ('Водонагреватель', 'ГВС', 3.0),
            ('Освещение (основное)', 'Свет', 0.5),
            ('Микроволновка', 'Кухня', 1.2),
        ]

        devices = []
        for name, dtype, rated_power in devices_data:
            device = Device.objects.create(
                name=name,
                device_type=dtype,
                status=random.choice(['online', 'online', 'online', 'offline']),
                power_state=random.choice(['on', 'on', 'on', 'off']),
                current_power=random.uniform(0.1, rated_power) if random.choice([True, False]) else 0,
                rated_power=rated_power
            )
            devices.append(device)
            self.stdout.write(self.style.SUCCESS(f'Создано устройство: {name}'))

        # Добавляем ошибки
        water_heater = Device.objects.get(name='Водонагреватель')
        DeviceError.objects.create(
            device=water_heater,
            error_type='Offline Error',
            description='Устройство оффлайн',
            severity='high'
        )

        ac = Device.objects.get(name='Кондиционер')
        DeviceError.objects.create(
            device=ac,
            error_type='Maintenance Required',
            description='Требуется обслуживание фильтра',
            severity='medium'
        )

        self.stdout.write(self.style.SUCCESS('Созданы ошибки'))

        # Генерируем исторические данные
        today = timezone.now().date()

        for device in devices:
            for i in range(30):
                date = today - timedelta(days=i)

                daily_energy = 0
                peak_power = 0
                total_power = 0

                for hour in range(24):
                    if device.status == 'online' and device.power_state == 'on':
                        power = random.uniform(device.rated_power * 0.3, device.rated_power)
                    else:
                        power = random.uniform(0, device.rated_power * 0.1)

                    daily_energy += power / 24
                    peak_power = max(peak_power, power)
                    total_power += power

                    timestamp = timezone.make_aware(
                        timezone.datetime.combine(date, timezone.datetime.min.time())
                    ) + timedelta(hours=hour)

                    EnergyConsumption.objects.create(
                        device=device,
                        power=power,
                        energy=power / 24
                    )

                avg_power = total_power / 24
                cost = daily_energy * 7.22

                DailyStatistics.objects.create(
                    device=device,
                    date=date,
                    total_energy=daily_energy,
                    avg_power=avg_power,
                    peak_power=peak_power,
                    cost=cost
                )

            self.stdout.write(self.style.SUCCESS(f'Сгенерированы данные для: {device.name}'))

        # Добавляем историю действий для forgotten-detection
        now = timezone.now()
        for device in devices:
            action_time = now - timedelta(hours=random.choice([8, 10, 14, 18]))
            DeviceAction.objects.create(
                device=device,
                action_type='power_on',
                details={'source': 'initial'},
                timestamp=action_time,
            )
        self.stdout.write(self.style.SUCCESS('Созданы истории действий'))

        self.stdout.write(self.style.SUCCESS('Данные успешно сгенерированы!'))
