from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .tasks import generate_report
from uuid import uuid4
from datetime import datetime
import pandas as pd
from django.conf import settings
from .models import *
import os

class TriggerReportView(APIView):
    def post(self, request):
        report_id = str(uuid4())
        generate_report.delay(report_id)  # Fire off the task
        return Response(TriggerReportSerializer({'report_id': report_id}).data, status=status.HTTP_200_OK)

class GetReportView(APIView):
    def get(self, request, report_id):
        path = os.path.join(settings.BASE_DIR, 'reports', f'{report_id}.csv')
        if not os.path.exists(path):
            return Response(GetReportSerializer({'status': 'Running'}).data, status=status.HTTP_200_OK)
        with open(path, 'r') as f:
            csv_content = f.read()
        return Response(GetReportSerializer({'status': 'Complete', 'csv_content': csv_content}).data, status=status.HTTP_200_OK)

import os
import pandas as pd
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Timezone, BusinessHour, StoreStatus
from .serializers import TimezoneSerializer, BusinessHourSerializer, StoreStatusSerializer


DATA_PATH = "store-monitoring-data"


class LoadDataView(APIView):
    def post(self, request):
        try:
            messages = []

            # Load timezones
            tz_file = os.path.join(DATA_PATH, "timezones.csv")
            if os.path.exists(tz_file):
                df = pd.read_csv(tz_file)
                for _, row in df.iterrows():
                    Timezone.objects.create(
                        store_id=str(row["store_id"]),
                        timezone_str=row["timezone_str"]
                    )
                messages.append("Loaded timezones")
            else:
                messages.append("timezones.csv missing")

            # Load business hours
            hours_file = os.path.join(DATA_PATH, "menu_hours.csv")
            if os.path.exists(hours_file):
                df = pd.read_csv(hours_file)
                for _, row in df.iterrows():
                    start = datetime.strptime(row["start_time_local"], "%H:%M:%S").time()
                    end = datetime.strptime(row["end_time_local"], "%H:%M:%S").time()
                    BusinessHour.objects.create(
                        store_id=str(row["store_id"]),
                        day_of_week=row["dayOfWeek"],
                        start_time_local=start,
                        end_time_local=end,
                    )
                messages.append("Loaded business hours")
            else:
                messages.append("menu_hours.csv missing")

            # Load store status
            status_file = os.path.join(DATA_PATH, "store_status.csv")
            if os.path.exists(status_file):
                df = pd.read_csv(status_file)
                for _, row in df.iterrows():
                    fmt = "%Y-%m-%d %H:%M:%S.%f %Z" if "." in row["timestamp_utc"] else "%Y-%m-%d %H:%M:%S %Z"
                    ts = datetime.strptime(row["timestamp_utc"], fmt)
                    StoreStatus.objects.create(
                        store_id=str(row["store_id"]),
                        timestamp_utc=ts,
                        status=row["status"],
                    )
                messages.append("Loaded store status")
            else:
                messages.append("store_status.csv missing")

            return Response({"message": ", ".join(messages)}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CleanDBView(APIView):
    def delete(self, request):
        try:
            StoreStatus.objects.all().delete()
            BusinessHour.objects.all().delete()
            Timezone.objects.all().delete()
            return Response({"message": "Database cleared"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DataView(APIView):
    def get(self, request, table):
        try:
            if table == "timezone":
                data = TimezoneSerializer(Timezone.objects.all(), many=True).data
            elif table == "businesshour":
                data = BusinessHourSerializer(BusinessHour.objects.all(), many=True).data
            elif table == "storestatus":
                data = StoreStatusSerializer(StoreStatus.objects.all(), many=True).data
            else:
                return Response(
                    {"message": "Invalid table. Choose among timezone/ businesshour/storestatus"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
