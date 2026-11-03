from django.urls import path
from .views import DashboardView, ReportView
urlpatterns=[path('dashboard/',DashboardView.as_view()),path('reports/<str:kind>.<str:format>/',ReportView.as_view())]
