from celery import shared_task
from django.db.models import Max
from datetime import datetime, timedelta, time
import pytz
import csv
import os
from store_monitor.models import StoreStatus, BusinessHour, Timezone
from django.conf import settings
from django.core.cache import cache
import io

# Calculate minutes within business hours between two UTC timestamps
def business_minutes(start_utc, end_utc, tz, business_hours):
    if start_utc >= end_utc:
        return 0
    local_start = start_utc.astimezone(tz)
    local_end = end_utc.astimezone(tz)
    total_minutes = 0
    current = local_start
    while current < local_end:
        day = current.weekday()
        next_day = (current + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        if day in business_hours:
            start_time, end_time = business_hours[day]
            day_start = current.replace(hour=start_time.hour, minute=start_time.minute)
            day_end = current.replace(hour=end_time.hour, minute=end_time.minute)
            b_start = max(day_start, current)
            b_end = min(day_end, min(local_end, next_day))
            if b_start < b_end:
                total_minutes += (b_end - b_start).total_seconds() / 60
        current = next_day
    return total_minutes

# Compute uptime/downtime by interpolating polls
def compute_uptime_downtime(period_start, period_end, tz, business_hours, polls):
    if not polls:
        # No polls? All downtime during business hours
        return 0, business_minutes(period_start, period_end, tz, business_hours)
    
    # Find the status just before the period
    prev_time = None
    prev_status = None
    for t, active in polls:
        if t <= period_start:
            prev_time, prev_status = t, active
        else:
            break
    
    # If no prior status, use the first poll’s status
    if prev_status is None and polls:
        prev_status = polls[0][1]
    elif prev_status is None:
        # No polls at all? All downtime
        return 0, business_minutes(period_start, period_end, tz, business_hours)

    # Build intervals: each poll extends its status to the next poll
    intervals = []
    current_time = period_start
    i = next((idx for idx, (t, _) in enumerate(polls) if t > period_start), len(polls))
    if prev_status is not None:
        for j in range(i - 1 if prev_time and prev_time <= period_start else i, len(polls)):
            t, active = polls[j]
            intervals.append((current_time, t, prev_status))
            current_time, prev_status = t, active
    if current_time < period_end:
        intervals.append((current_time, period_end, prev_status))
    
    # Sum up minutes for uptime/downtime
    uptime, downtime = 0, 0
    for start, end, active in intervals:
        bus_min = business_minutes(start, end, tz, business_hours)
        if active:
            uptime += bus_min
        else:
            downtime += bus_min
    return uptime, downtime

# Helper: cache per store report
def get_store_report(store_id, now_utc, last_hour, last_day, last_week, tz, business_hours, polls):
    cache_key = f"store_report:{store_id}:{now_utc.isoformat()}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    u_h_min, d_h_min = compute_uptime_downtime(last_hour, now_utc, tz, business_hours, polls)
    u_d_min, d_d_min = compute_uptime_downtime(last_day, now_utc, tz, business_hours, polls)
    u_w_min, d_w_min = compute_uptime_downtime(last_week, now_utc, tz, business_hours, polls)

    row = [
        store_id,
        round(u_h_min), round(u_d_min / 60), round(u_w_min / 60),
        round(d_h_min), round(d_d_min / 60), round(d_w_min / 60)
    ]

    # Cache for 1 hour (matches polling frequency)
    cache.set(cache_key, row, timeout=3600)
    return row


@shared_task
def generate_report(report_id):
    # Cache full report first (so repeated requests don’t hit DB)
    report_cache_key = f"report:{report_id}"
    cached_report = cache.get(report_cache_key)
    if cached_report:
        path = os.path.join(settings.BASE_DIR, 'reports', f'{report_id}.csv')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', newline='') as f:
            f.write(cached_report)
        return

    # Get latest timestamp as "now"
    now_utc = StoreStatus.objects.aggregate(Max('timestamp_utc'))['timestamp_utc__max']
    if not now_utc:
        path = os.path.join(settings.BASE_DIR, 'reports', f'{report_id}.txt')
        with open(path, 'w') as f:
            f.write('No data')
        return

    # Time ranges
    last_hour = now_utc - timedelta(hours=1)
    last_day = now_utc - timedelta(days=1)
    last_week = now_utc - timedelta(days=7)
    store_ids = StoreStatus.objects.values_list('store_id', flat=True).distinct()

    # Prepare CSV in-memory
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        'store_id',
        'uptime_last_hour',
        'uptime_last_day',
        'uptime_last_week',
        'downtime_last_hour',
        'downtime_last_day',
        'downtime_last_week'
    ])

    for store_id in store_ids:
        # Timezone fallback
        tz_obj = Timezone.objects.filter(store_id=store_id).first()
        tz = pytz.timezone(tz_obj.timezone_str if tz_obj else 'America/Chicago')

        # Business hours fallback
        hours = BusinessHour.objects.filter(store_id=store_id)
        business_hours = {h.day_of_week: (h.start_time_local, h.end_time_local) for h in hours}
        if not business_hours:
            business_hours = {d: (time(0, 0), time(23, 59)) for d in range(7)}

        # Polls
        polls = StoreStatus.objects.filter(store_id=store_id).order_by('timestamp_utc').values('timestamp_utc', 'status')
        polls = [(p['timestamp_utc'], p['status'] == 'active') for p in polls]

        # Compute (cached per store)
        row = get_store_report(store_id, now_utc, last_hour, last_day, last_week, tz, business_hours, polls)
        writer.writerow(row)

    # Save CSV output to memory + cache + file
    csv_content = buffer.getvalue()
    buffer.close()

    cache.set(report_cache_key, csv_content, timeout=3600)

    path = os.path.join(settings.BASE_DIR, 'reports', f'{report_id}.csv')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='') as f:
        f.write(csv_content)
