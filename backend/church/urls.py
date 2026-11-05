from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ChurchProfileView, ServiceScheduleViewSet

router = DefaultRouter()
router.register('church/schedules', ServiceScheduleViewSet, basename='church-schedule')

urlpatterns = [
    path('church/', ChurchProfileView.as_view(), name='church-profile'),
    *router.urls,
]
