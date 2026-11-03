from rest_framework.routers import DefaultRouter
from .views import DonationViewSet
router = DefaultRouter(); router.register('donations', DonationViewSet, basename='donation')
urlpatterns = router.urls
