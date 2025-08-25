from django.urls import path,re_path
from .views import *
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Store Monitoring API",
        default_version="v1",
        description="API for monitoring store uptime/downtime and reports",
        contact=openapi.Contact(email="you@example.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('trigger_report/', TriggerReportView.as_view(), name='trigger_report'),
    path('get_report/<str:report_id>/', GetReportView.as_view(), name='get_report'),
    path('data/', DataCollectionView.as_view(), name='data_collection'), 
    path('data/<str:table>/', DataTableView.as_view(), name='data_table'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]