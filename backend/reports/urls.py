from django.urls import path

from .views import DashboardView, ReportView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('reports/<slug:report>/', ReportView.as_view(), name='report'),
]
