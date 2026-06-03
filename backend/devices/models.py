from django.db import models
from django.utils import timezone


class Device(models.Model):
    STATUS_CHOICES = [
        ('online', 'Онлайн'),
        ('offline', 'Офлайн'),
    ]
    
    POWER_STATE_CHOICES = [
        ('on', 'Включено'),
        ('off', 'Выключено'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    device_type = models.CharField(max_length=50, verbose_name='Тип устройства')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='Статус')
    power_state = models.CharField(max_length=20, choices=POWER_STATE_CHOICES, verbose_name='Состояние')
    current_power = models.FloatField(default=0, verbose_name='Текущая мощность (кВт)')
    rated_power = models.FloatField(verbose_name='Номинальная мощность (кВт)')
    last_update = models.DateTimeField(auto_now=True, verbose_name='Последнее обновление')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['last_update']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'Устройство'
        verbose_name_plural = 'Устройства'
    
    def __str__(self):
        return self.name


class DeviceError(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Низкая'),
        ('medium', 'Средняя'),
        ('high', 'Высокая'),
    ]
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='errors', verbose_name='Устройство')
    error_type = models.CharField(max_length=100, verbose_name='Тип ошибки')
    description = models.TextField(verbose_name='Описание')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, verbose_name='Серьезность')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='Решено')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ошибка устройства'
        verbose_name_plural = 'Ошибки устройств'
    
    def __str__(self):
        return f"{self.device.name} - {self.error_type}"


class DeviceAction(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='actions', verbose_name='Устройство')
    action_type = models.CharField(max_length=50, verbose_name='Тип действия')
    details = models.JSONField(verbose_name='Детали')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время')
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'timestamp']),
        ]
        verbose_name = 'Действие устройства'
        verbose_name_plural = 'Действия устройств'
    
    def __str__(self):
        return f"{self.device.name} - {self.action_type}"

class Schedule(models.Model):
    ACTION_CHOICES = [
        ('on', 'Включить'),
        ('off', 'Отключить'),
    ]
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='schedules', verbose_name='Устройство')
    time = models.TimeField(verbose_name='Время выполнения')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name='Действие')
    enabled = models.BooleanField(default=True, verbose_name='Активно')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    
    class Meta:
        ordering = ['time']
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'
        indexes = [
            models.Index(fields=['device', 'enabled']),
            models.Index(fields=['time']),
        ]
    
    def __str__(self):
        return f"{self.device.name} - {self.time} ({self.action})"


class PresetSchedule(models.Model):
    CATEGORY_CHOICES = [
        ('energy_saving', 'Экономия энергии'),
        ('comfort', 'Комфорт'),
        ('balanced', 'Сбалансированное'),
        ('24h', '24 часа'),
    ]

    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='Категория')
    icon = models.CharField(max_length=10, default='📅', verbose_name='Иконка')
    estimated_savings = models.FloatField(default=0, verbose_name='Ожидаемая экономия (%)')
    recommended_for = models.CharField(max_length=200, blank=True, verbose_name='Рекомендовано для')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        ordering = ['name']
        verbose_name = 'Пресет расписания'
        verbose_name_plural = 'Пресеты расписаний'

    def __str__(self):
        return self.name


class PresetScheduleEntry(models.Model):
    ACTION_CHOICES = [
        ('on', 'Включить'),
        ('off', 'Отключить'),
    ]
    DAY_CHOICES = [
        ('monday', 'Понедельник'),
        ('tuesday', 'Вторник'),
        ('wednesday', 'Среда'),
        ('thursday', 'Четверг'),
        ('friday', 'Пятница'),
        ('saturday', 'Суббота'),
        ('sunday', 'Воскресенье'),
    ]

    preset_schedule = models.ForeignKey(
        PresetSchedule, on_delete=models.CASCADE,
        related_name='entries', verbose_name='Пресет',
    )
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES, verbose_name='День недели')
    start_time = models.TimeField(verbose_name='Начало')
    end_time = models.TimeField(verbose_name='Конец')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name='Действие')

    class Meta:
        ordering = ['day_of_week', 'start_time']
        verbose_name = 'Запись пресета'
        verbose_name_plural = 'Записи пресетов'

    def __str__(self):
        return f"{self.preset_schedule.name} - {self.day_of_week} {self.start_time}-{self.end_time}"