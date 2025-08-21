from rest_framework import serializers
from .models import *

class TimezoneSerializer(serializers.Serializer):
     class Meta:
        model = Timezone
        fields = ['store_id', 'timezone_str']

class BusinessHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessHour
        fields = ['store_id', 'day_of_week', 'start_time_local', 'end_time_local']

class StoreStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreStatus
        fields = ['store_id', 'timestamp_utc', 'status']

class TriggerReportSerializer(serializers.Serializer):
    report_id = serializers.CharField()

class GetReportSerializer(serializers.Serializer):
    status = serializers.CharField()
    csv_content = serializers.CharField(required=False)