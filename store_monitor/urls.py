from django.urls import path
from .views import *

urlpatterns = [
    # Reports resource
    path('reports/', TriggerReportView.as_view(), name='reports'),  # POST to create/trigger a report
    path('reports/<str:report_id>/', GetReportView.as_view(), name='report-detail'),  # GET report status/content

    # Domain resources (read-only lists)
    path('timezones/', DataView.as_view(), {'table': 'timezone'}, name='timezones-list'),
    path('business-hours/', DataView.as_view(), {'table': 'businesshour'}, name='business-hours-list'),
    path('store-statuses/', DataView.as_view(), {'table': 'storestatus'}, name='store-statuses-list'),

    # Data management
    path('data/', CleanDBView.as_view(), name='data'),  # DELETE to clear all imported data
    path('data-imports/', LoadDataView.as_view(), name='data-imports'),  # POST to load data from CSVs
]