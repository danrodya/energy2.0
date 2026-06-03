from rest_framework import serializers
from .models import EnergyConsumption, DailyStatistics, AnomalyAlert, SavingRecommendation, TimeOverride


class EnergyConsumptionSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)

    class Meta:
        model = EnergyConsumption
        fields = ['id', 'device', 'device_name', 'power', 'energy', 'timestamp']


class DailyStatisticsSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)

    class Meta:
        model = DailyStatistics
        fields = ['id', 'device', 'device_name', 'date', 'total_energy',
                  'avg_power', 'peak_power', 'cost']


class AnomalyAlertSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    ml_score = serializers.SerializerMethodField()

    class Meta:
        model = AnomalyAlert
        fields = ['id', 'device', 'device_name', 'anomaly_type',
                  'severity', 'description', 'current_value',
                  'expected_value', 'detected_at', 'resolved_at', 'ml_score']

    def get_ml_score(self, obj):
        return None


class TimeOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeOverride
        fields = ['simulated_time']


class SavingRecommendationSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)

    class Meta:
        model = SavingRecommendation
        fields = ['id', 'device', 'device_name', 'scenario_type',
                  'title', 'description', 'current_cost', 'estimated_savings',
                  'savings_percent', 'implemented', 'created_at']
