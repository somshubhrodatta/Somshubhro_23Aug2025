from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .tasks import generate_report
from uuid import uuid4
from datetime import datetime
import pandas as pd
from django.conf import settings
from django.db import transaction
from .models import *
import os
from .models import Timezone, BusinessHour, StoreStatus
from .serializers import TimezoneSerializer, BusinessHourSerializer, StoreStatusSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class TriggerReportView(APIView):
    @swagger_auto_schema(
        operation_description="Trigger a new report generation task",
        responses={200: openapi.Response("Report triggered", TriggerReportSerializer,examples={
                    "application/json": {
                        "report_id": "a1b2c3d4-e5f6-7890-1234-56789abcdef0"
                    }
                })}
    )
    def post(self, request):
        report_id = str(uuid4())
        generate_report.delay(report_id)
        return Response(TriggerReportSerializer({'report_id': report_id}).data, status=status.HTTP_200_OK)

class GetReportView(APIView):
    @swagger_auto_schema(
        operation_description="Get report status or download report",
        responses={
            200: "Returns 'Running' or 'Complete' with CSV file",
            404: "Report not found"
        }
    )
    def get(self, request, report_id):
        path = os.path.join(settings.BASE_DIR, 'reports', f'{report_id}.csv')
        if not os.path.exists(path):
            return Response(GetReportSerializer({'status': 'Running'}).data, status=status.HTTP_200_OK)
        with open(path, 'r') as f:
            csv_content = f.read()
        return Response(GetReportSerializer({'status': 'Complete', 'csv_content': csv_content}).data, status=status.HTTP_200_OK)



DATA_PATH = "store-monitoring-data"


class DataCollectionView(APIView):
    def post(self, request):
        try:
            messages = []

            # Load timezones
            tz_file = os.path.join(DATA_PATH, "timezones.csv")
            if os.path.exists(tz_file):
                df = pd.read_csv(tz_file)
                objs = [Timezone(store_id=str(r["store_id"]), timezone_str=r["timezone_str"]) for _, r in df.iterrows()]
                self._bulk_insert(Timezone, objs)
                messages.append(f"Loaded {len(objs)} timezones")
            else:
                messages.append("timezones.csv missing")

            # Load business hours
            hours_file = os.path.join(DATA_PATH, "menu_hours.csv")
            if os.path.exists(hours_file):
                df = pd.read_csv(hours_file)
                objs = []
                for _, r in df.iterrows():
                    start = datetime.strptime(r["start_time_local"], "%H:%M:%S").time()
                    end = datetime.strptime(r["end_time_local"], "%H:%M:%S").time()
                    objs.append(BusinessHour(
                        store_id=str(r["store_id"]),
                        day_of_week=int(r["dayOfWeek"]),
                        start_time_local=start,
                        end_time_local=end,
                    ))
                self._bulk_insert(BusinessHour, objs)
                messages.append(f"Loaded {len(objs)} business hours")
            else:
                messages.append("menu_hours.csv missing")

            # Load store status
            status_file = os.path.join(DATA_PATH, "store_status.csv")
            if os.path.exists(status_file):
                df = pd.read_csv(status_file)
                objs = []
                for _, r in df.iterrows():
                    fmt = "%Y-%m-%d %H:%M:%S.%f %Z" if "." in r["timestamp_utc"] else "%Y-%m-%d %H:%M:%S %Z"
                    ts = datetime.strptime(r["timestamp_utc"], fmt)
                    objs.append(StoreStatus(
                        store_id=str(r["store_id"]),
                        timestamp_utc=ts,
                        status=r["status"],
                    ))
                self._bulk_insert(StoreStatus, objs, batch_size=2000)
                messages.append(f"Loaded {len(objs)} store status records")
            else:
                messages.append("store_status.csv missing")

            return Response({"message": ", ".join(messages)}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        try:
            StoreStatus.objects.all().delete()
            BusinessHour.objects.all().delete()
            Timezone.objects.all().delete()
            return Response({"message": "Database cleared"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _bulk_insert(self, model, objs, batch_size=1000):
        """Helper for fast batch inserts"""
        if objs:
            with transaction.atomic():
                model.objects.bulk_create(objs, batch_size=batch_size, ignore_conflicts=True)


class DataTableView(APIView):

    @swagger_auto_schema(
        operation_description="Get all records from a table",
        manual_parameters=[
            openapi.Parameter(
                "table",
                openapi.IN_PATH,
                description="Table name (timezone, businesshour, storestatus)",
                type=openapi.TYPE_STRING,
                required=True,
                enum=["timezone", "businesshour", "storestatus"],  # ✅ restrict values
            )
        ],
        responses={
            200: openapi.Response(
                description="List of records",
                examples={
                    "application/json": [
                        {"store_id": "1", "timezone_str": "America/Chicago"},  # timezone sample
                        {"store_id": "2", "day_of_week": 0, "start_time_local": "09:00:00", "end_time_local": "17:00:00"},  # businesshour sample
                        {"store_id": "3", "timestamp_utc": "2023-05-10T10:14:00Z", "status": "active"}  # storestatus sample
                    ]
                }
            ),
            400: openapi.Response(description="Invalid table name"),
            500: openapi.Response(description="Server error"),
        }
    )
    def get(self, request, table):
        try:
            if table == "timezone":
                data = TimezoneSerializer(Timezone.objects.all()[:100], many=True).data
            elif table == "businesshour":
                data = BusinessHourSerializer(BusinessHour.objects.all()[:100], many=True).data
            elif table == "storestatus":
                data = StoreStatusSerializer(StoreStatus.objects.all()[:100], many=True).data
            else:
                return Response(
                    {"message": "Invalid table. Choose among timezone/businesshour/storestatus"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
