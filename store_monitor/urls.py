from django.urls import path
from .views import *

urlpatterns = [
    path('trigger_report/', TriggerReportView.as_view(), name='trigger_report'),
    path('get_report/<str:report_id>/', GetReportView.as_view(), name='get_report'),
    path('showdata/<str:table>',DataView.as_view(), name='show_data'),
    path('erase_data/',CleanDBView.as_view(),name='clean_db'),
    path('load_data/',LoadDataView.as_view(),name='load_from_csv')
]