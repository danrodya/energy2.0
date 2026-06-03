# Generated for PresetSchedule and PresetScheduleEntry

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0002_alter_device_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='PresetSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('category', models.CharField(choices=[
                    ('energy_saving', 'Экономия энергии'),
                    ('comfort', 'Комфорт'),
                    ('balanced', 'Сбалансированное'),
                    ('24h', '24 часа'),
                ], max_length=50, verbose_name='Категория')),
                ('icon', models.CharField(default='📅', max_length=10, verbose_name='Иконка')),
                ('estimated_savings', models.FloatField(default=0, verbose_name='Ожидаемая экономия (%)')),
                ('recommended_for', models.CharField(blank=True, max_length=200, verbose_name='Рекомендовано для')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
            ],
            options={
                'verbose_name': 'Пресет расписания',
                'verbose_name_plural': 'Пресеты расписаний',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PresetScheduleEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.CharField(choices=[
                    ('monday', 'Понедельник'),
                    ('tuesday', 'Вторник'),
                    ('wednesday', 'Среда'),
                    ('thursday', 'Четверг'),
                    ('friday', 'Пятница'),
                    ('saturday', 'Суббота'),
                    ('sunday', 'Воскресенье'),
                ], max_length=10, verbose_name='День недели')),
                ('start_time', models.TimeField(verbose_name='Начало')),
                ('end_time', models.TimeField(verbose_name='Конец')),
                ('action', models.CharField(choices=[('on', 'Включить'), ('off', 'Отключить')], max_length=10, verbose_name='Действие')),
                ('preset_schedule', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='entries',
                    to='devices.presetschedule',
                    verbose_name='Пресет',
                )),
            ],
            options={
                'verbose_name': 'Запись пресета',
                'verbose_name_plural': 'Записи пресетов',
                'ordering': ['day_of_week', 'start_time'],
            },
        ),
    ]
