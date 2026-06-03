from django.contrib import admin
from .models import EnergyConsumption, DailyStatistics, AnomalyAlert, SavingRecommendation, AnomalyLog


@admin.register(EnergyConsumption)
class EnergyConsumptionAdmin(admin.ModelAdmin):
    list_display = ['device', 'power', 'energy', 'timestamp']
    list_filter = ['device', 'timestamp']
    search_fields = ['device__name']
    readonly_fields = ['timestamp']


@admin.register(DailyStatistics)
class DailyStatisticsAdmin(admin.ModelAdmin):
    list_display = ['device', 'date', 'total_energy', 'avg_power', 'peak_power', 'cost']
    list_filter = ['date', 'device']
    search_fields = ['device__name']


@admin.register(AnomalyAlert)
class AnomalyAlertAdmin(admin.ModelAdmin):
    list_display = ['device', 'anomaly_type', 'severity', 'detected_at', 'resolved_at']
    list_filter = ['anomaly_type', 'severity', 'resolved_at']
    search_fields = ['device__name', 'description']
    readonly_fields = ['detected_at']


@admin.register(SavingRecommendation)
class SavingRecommendationAdmin(admin.ModelAdmin):
    list_display = ['device', 'scenario_type', 'title', 'estimated_savings', 'savings_percent', 'implemented']
    list_filter = ['scenario_type', 'implemented']
    search_fields = ['device__name', 'title']


@admin.register(AnomalyLog)
class AnomalyLogAdmin(admin.ModelAdmin):
    list_display = ['device', 'anomaly_type', 'load_ratio', 'created_at']
    list_filter = ['anomaly_type', 'created_at']
    search_fields = ['device__name', 'description']
    readonly_fields = ['created_at']
