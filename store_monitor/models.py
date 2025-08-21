from django.db import models

# Store poll data: store_id, timestamp (UTC), and status (active/inactive)
class StoreStatus(models.Model):
    store_id = models.CharField(max_length=50)
    timestamp_utc = models.DateTimeField()
    status = models.CharField(max_length=10)

    class Meta:
        indexes = [
            models.Index(fields=['store_id', 'timestamp_utc']),  # Speed up queries
        ]

# Business hours: store_id, day (0=Monday, 6=Sunday), start/end times (local)
class BusinessHour(models.Model):
    store_id = models.CharField(max_length=50)
    day_of_week = models.IntegerField()
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()

# Timezone mapping: store_id to timezone (default: America/Chicago)
class Timezone(models.Model):
    store_id = models.CharField(max_length=50)
    timezone_str = models.CharField(max_length=50)