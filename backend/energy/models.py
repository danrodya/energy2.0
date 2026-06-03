from django.db import models
from devices.models import Device


class EnergyConsumption(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='consumption', verbose_name='Устройство')
    power = models.FloatField(verbose_name='Мощность (кВт)')
    energy = models.FloatField(verbose_name='Энергия (кВт·ч)')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время')
    
    class Meta:
        indexes = [
            models.Index(fields=['device', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['device']),
        ]
        ordering = ['-timestamp']
        verbose_name = 'Потребление энергии'
        verbose_name_plural = 'Потребления энергии'
    
    def __str__(self):
        return f"{self.device.name} - {self.power}кВ"


class DailyStatistics(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='daily_stats', verbose_name='Устройство')
    date = models.DateField(verbose_name='Дата')
    total_energy = models.FloatField(verbose_name='Общая энергия (кВт·ч)')
    avg_power = models.FloatField(verbose_name='Средняя мощность (кВт)')
    peak_power = models.FloatField(verbose_name='Пиковая мощность (кВт)')
    cost = models.FloatField(verbose_name='Стоимость (₽)')
    
    class Meta:
        unique_together = ['device', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['device', 'date']),
        ]
        verbose_name = 'Суточная статистика'
        verbose_name_plural = 'Суточные статистики'
    
    def __str__(self):
        return f"{self.device.name} - {self.date}"


class AnomalyAlert(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Низкая'),
        ('medium', 'Средняя'),
        ('high', 'Высокая'),
    ]
    TYPE_CHOICES = [
        ('overload', 'Перегрузка'),
        ('forgotten', 'Забытое устройство'),
        ('night_work', 'Ночная работа'),
        ('high_baseline', 'Высокий фон'),
        ('spike', 'Резкий скачок'),
    ]

    device = models.ForeignKey('devices.Device', on_delete=models.CASCADE,
                               related_name='anomalies', verbose_name='Устройство')
    anomaly_type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name='Тип')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, verbose_name='Серьёзность')
    description = models.TextField(verbose_name='Описание')
    current_value = models.FloatField(default=0, verbose_name='Текущее значение')
    expected_value = models.FloatField(default=0, verbose_name='Ожидаемое значение')
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name='Обнаружено')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='Решено')

    class Meta:
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['device', 'resolved_at']),
            models.Index(fields=['severity']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['device', 'anomaly_type'],
                condition=models.Q(resolved_at__isnull=True),
                name='uq_anomaly_device_type_unresolved'
            ),
        ]
        verbose_name = 'Аномалия'
        verbose_name_plural = 'Аномалии'

    def __str__(self):
        return f"{self.device.name} - {self.get_anomaly_type_display()}"


class SavingRecommendation(models.Model):
    TYPE_CHOICES = [
        ('schedule', 'Настройка расписания'),
        ('night_shift', 'Перенос на ночь'),
        ('replacement', 'Замена устройства'),
        ('preset', 'Готовый сценарий'),
    ]

    device = models.ForeignKey('devices.Device', on_delete=models.CASCADE,
                               related_name='recommendations', verbose_name='Устройство')
    scenario_type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name='Тип')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    current_cost = models.FloatField(default=0, verbose_name='Текущая стоимость (₽/мес)')
    estimated_savings = models.FloatField(default=0, verbose_name='Экономия (₽/мес)')
    savings_percent = models.FloatField(default=0, verbose_name='Экономия (%)')
    implemented = models.BooleanField(default=False, verbose_name='Применено')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        ordering = ['-estimated_savings']
        verbose_name = 'Рекомендация'
        verbose_name_plural = 'Рекомендации'

    def __str__(self):
        return f"{self.device.name} - {self.title}"


class AnomalyLog(models.Model):
    TYPE_CHOICES = [
        ('overload', 'Перегрузка'),
        ('night_work', 'Ночная работа'),
        ('forgotten', 'Забытое устройство'),
    ]

    device = models.ForeignKey('devices.Device', on_delete=models.CASCADE,
                               related_name='anomaly_logs', verbose_name='Устройство')
    anomaly_type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name='Тип')
    load_ratio = models.FloatField(default=0, verbose_name='Загрузка (%)')
    description = models.TextField(verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', 'created_at']),
            models.Index(fields=['anomaly_type']),
        ]
        verbose_name = 'Лог аномалии'
        verbose_name_plural = 'Логи аномалий'

    def __str__(self):
        return f"{self.device.name} - {self.get_anomaly_type_display()} ({self.created_at:%H:%M})"


class TimeOverride(models.Model):
    simulated_time = models.DateTimeField(null=True, blank=True, verbose_name='Симулированное время')

    class Meta:
        verbose_name = 'Переопределение времени'
        verbose_name_plural = 'Переопределение времени'
