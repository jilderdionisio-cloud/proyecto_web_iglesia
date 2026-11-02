from rest_framework.routers import DefaultRouter

from .views import AttendanceHistoryViewSet, AttendanceSessionViewSet

router = DefaultRouter()
router.register('attendance-sessions', AttendanceSessionViewSet, basename='attendance-session')
router.register('attendance-history', AttendanceHistoryViewSet, basename='attendance-history')

urlpatterns = router.urls
