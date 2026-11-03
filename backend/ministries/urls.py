from rest_framework.routers import DefaultRouter

from .views import MinistryViewSet, MinistryActivityViewSet

router = DefaultRouter()
router.register('ministries', MinistryViewSet, basename='ministry')
router.register('ministry-activities', MinistryActivityViewSet, basename='ministry-activity')

urlpatterns = router.urls
