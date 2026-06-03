from django.core.management.base import BaseCommand
from devices.models import PresetSchedule, PresetScheduleEntry
from datetime import time

class Command(BaseCommand):
    help = 'Create preset schedules'

    def handle(self, *args, **options):
        # Удалить старые расписания
        PresetSchedule.objects.all().delete()

        # 1. Расписание "Экономия энергии"
        energy_saving = PresetSchedule.objects.create(
            name='Экономия энергии',
            description='Минимальное потребление, оптимизировано для снижения расходов',
            category='energy_saving',
            icon='💚',
            estimated_savings=35.0,
            recommended_for='холодильник, водонагреватель'
        )

        # Записи для экономии энергии
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            PresetScheduleEntry.objects.create(
                preset_schedule=energy_saving,
                day_of_week=day,
                start_time=time(6, 0),
                end_time=time(22, 0),
                action='on'
            )
            PresetScheduleEntry.objects.create(
                preset_schedule=energy_saving,
                day_of_week=day,
                start_time=time(22, 0),
                end_time=time(6, 0),
                action='off'
            )

        for day in ['saturday', 'sunday']:
            PresetScheduleEntry.objects.create(
                preset_schedule=energy_saving,
                day_of_week=day,
                start_time=time(8, 0),
                end_time=time(23, 0),
                action='on'
            )

        # 2. Расписание "Комфорт"
        comfort = PresetSchedule.objects.create(
            name='Комфорт',
            description='Круглосуточная работа для максимального комфорта',
            category='comfort',
            icon='☀️',
            estimated_savings=0.0,
            recommended_for='кондиционер, освещение'
        )

        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            PresetScheduleEntry.objects.create(
                preset_schedule=comfort,
                day_of_week=day,
                start_time=time(0, 0),
                end_time=time(23, 59),
                action='on'
            )

        # 3. Расписание "Сбалансированное"
        balanced = PresetSchedule.objects.create(
            name='Сбалансированное',
            description='Оптимальный баланс между комфортом и экономией',
            category='balanced',
            icon='⚖️',
            estimated_savings=15.0,
            recommended_for='все устройства'
        )

        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            # Работа в рабочие дни
            PresetScheduleEntry.objects.create(
                preset_schedule=balanced,
                day_of_week=day,
                start_time=time(7, 0),
                end_time=time(23, 0),
                action='on'
            )
            PresetScheduleEntry.objects.create(
                preset_schedule=balanced,
                day_of_week=day,
                start_time=time(23, 0),
                end_time=time(7, 0),
                action='off'
            )

        for day in ['saturday', 'sunday']:
            # Выходные
            PresetScheduleEntry.objects.create(
                preset_schedule=balanced,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(22, 0),
                action='on'
            )

        # 4. Расписание "24 часа"
        schedule_24h = PresetSchedule.objects.create(
            name='24 часа',
            description='Устройство работает 24 часа в сутки, 7 дней в неделю',
            category='24h',
            icon='⏰',
            estimated_savings=0.0,
            recommended_for='холодильник, системы безопасности'
        )

        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            PresetScheduleEntry.objects.create(
                preset_schedule=schedule_24h,
                day_of_week=day,
                start_time=time(0, 0),
                end_time=time(23, 59),
                action='on'
            )

        self.stdout.write(self.style.SUCCESS('Successfully created preset schedules'))